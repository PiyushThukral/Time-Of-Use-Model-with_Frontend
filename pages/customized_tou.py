def run(output_folder):
    import gurobipy as gp
    import matplotlib.pyplot as plt
    from gurobipy import GRB
    import numpy as np
    # Show all columns in display
    import pandas as pd
    pd.set_option('display.max_columns', None)

    import warnings
    warnings.filterwarnings('ignore')
    np.random.seed(42)
    import gc
    gc.collect()

    # Define your output Excel file path
    output_file = f"{output_folder}/output_file.xlsx"  # Change this to your desired path
    customer_data = f"{output_folder}/consumer_data_demo.xlsx"
    model_input_file = f"{output_folder}/model_settings_file.xlsx"
    
    # Read model parameters
    model_parameters = pd.read_excel(f"{model_input_file}", sheet_name= "model_parameters")  # Your file with cutoffs
    N = int(model_parameters[model_parameters['parameters'] == "number_of_scenarios"]['parameter_value'].values)
    run_CVar_model = int(model_parameters[model_parameters['parameters'] == "run_risk_weighted_Cvar"]['parameter_value'].values)
    alpha = float(model_parameters[model_parameters['parameters'] == "Cvar_alpha"]['parameter_value'].values)
    
    cvar_auxiliary_lower_limit = int(model_parameters[model_parameters['parameters'] == "cvar_auxiliary_lower_limit"]['parameter_value'].values)
    cvar_auxiliary_upper_limit = int(model_parameters[model_parameters['parameters'] == "cvar_auxiliary_upper_limit"]['parameter_value'].values)
    var_lower_limit = float(model_parameters[model_parameters['parameters'] == "var_lower_limit"]['parameter_value'].values)
    var_upper_limit = float(model_parameters[model_parameters['parameters'] == "var_upper_limit"]['parameter_value'].values)
    
    min_power_consumer_after_load_shifting = float(model_parameters[model_parameters['parameters'] == "min_power_consumer_after_load_shifting"]['parameter_value'].values)
    consumption_col_prefix = (model_parameters.loc[model_parameters['parameters'] == "consumption_col_prefix"]['parameter_value'].values[0])
    
    # Read bins
    tod_bins =pd.read_excel(f"{model_input_file}", sheet_name= "ToD_for_tariff")  # Your file with cutoffs
    
    total_blocks = tod_bins['define_cut_off_periods'].max()
    cutoffs = tod_bins['define_cut_off_periods'].values
    
    
    # Initialize start of first bin
    start = 1
    bins = []
    
    for cutoff in cutoffs:
        bins.append((start, int(cutoff)))
        start = int(cutoff) + 1
    
    # Number of bins
    T = len(bins)
    
    # Create Python ranges
    ranges = [range(s, e + 1) for s, e in bins]
    
    
    tod_continuity_settings = int(model_parameters[model_parameters['parameters'] == "tod_first_last_continuity_settings"]['parameter_value'].values)
    
    def merge_first_last_if_needed(ranges, tod_continuity_settings):
        if tod_continuity_settings == 1 and len(ranges) >= 2:
            # Combine values from first and last ranges into one list
            merged_values = list(ranges[0]) + list(ranges[-1])
    
            # Create new list: merged bin + middle ranges (unmodified)
            new_ranges = [merged_values] + ranges[1:-1]
            return new_ranges
        else:
            return ranges
    
    
    merged_ranges = merge_first_last_if_needed(ranges, tod_continuity_settings)
    
    for i, r in enumerate(merged_ranges, 1):
        print(f"Bin {i}: {list(r)}")
    
    T = len(merged_ranges)
    
    
    # Read TARIFF DATA
    tariff_data =pd.read_excel(f"{model_input_file}", sheet_name= "existing_tariffs")  # Your file with cutoffs
    
    # Stochasticity settings
    stochasticity =pd.read_excel(f"{model_input_file}", sheet_name= "stochasticity_settings")  # Your file with cutoffs
    
    std_dev_elasticity = float(stochasticity[stochasticity['stochasticity_variable'] == "elasticity"]['std_dev_value'].values)
    std_dev_market_prices = float(stochasticity[stochasticity['stochasticity_variable'] == "spot_market_prices"]['std_dev_value'].values)
    
    
    # Stochasticity settings
    
    demand_ramp_df =pd.read_excel(f"{model_input_file}", sheet_name= "demand_ramp")  # Your file with cutoffs
    
    demand_ramp_lower_limit = float(demand_ramp_df[demand_ramp_df['demand_ramp'] == "lower_limit"]['ramp_value'].values)
    demand_ramp_upper_limit = float(demand_ramp_df[demand_ramp_df['demand_ramp'] == "upper_limit"]['ramp_value'].values)
    
    demand_ramp = demand_ramp_upper_limit
    
    
    scenarios = N
    W=N
    probability = np.ones(scenarios)*[1/scenarios]
    
    
    # Tariff limits
    tariff_limits =pd.read_excel(f"{model_input_file}", sheet_name= "tariff_limits")  # Your file with cutoffs
    
    lower_limit_to_change_allowed = float(tariff_limits[tariff_limits['parameter_name'] == "lower_limit_to_change_allowed"]['parameter_value'].values)
    upper_limit_to_change_allowed = float(tariff_limits[tariff_limits['parameter_name'] == "upper_limit_to_change_allowed"]['parameter_value'].values)
    lower_limit_tariff = float(tariff_limits[tariff_limits['parameter_name'] == "lower_limit_tariff"]['parameter_value'].values)
    upper_limit_to_tariff = float(tariff_limits[tariff_limits['parameter_name'] == "upper_limit_to_tariff"]['parameter_value'].values)
    
    upper_limit_to_change_allowed
    
    
    env = gp.Env(empty=True)
    env.setParam("WLSACCESSID", "edcfd2fb-0fbd-4757-a9f9-d4ecf5906cba")
    env.setParam("WLSSECRET", "c6f06522-b031-4619-8047-3861ae3d6880")
    env.setParam("LICENSEID", 2659587)
    env.start()
    
    model = gp.Model("test", env=env)
    
    
    # Read bins
    consumer_load_norm_csv =pd.read_excel(f"{customer_data}", sheet_name= "consumer_data_demo")  # Your file with cutoffs
    
    
    ### Define number of unique consumers
    J = consumer_load_norm_csv['Consumer No'].nunique()
    
    def generate_consumption_column_groups(merged_ranges, consumption_col_prefix):
        column_groups = []
        for r in merged_ranges:
            if isinstance(r, range):
                hours = list(r)
            else:
                hours = r  # assume it's already a list
            group = [f"{consumption_col_prefix}{h}" for h in hours]
            column_groups.append(group)
        return column_groups
    
    column_groups = generate_consumption_column_groups(merged_ranges, consumption_col_prefix)
    
    for i, group in enumerate(column_groups, 1):
        print(f"Bin {i}: {group}")
    
    def add_total_period_columns(df, column_groups, T):
        total_group_columns = [f"Total_in_period_{h}" for h in range(1, T+1)]
        average_group_columns = [f"Average_in_period_{h}" for h in range(1, T+1)]
    
        for i, cols in enumerate(column_groups, start=1):
            df[f"Total_in_period_{i}"] = df[cols].sum(axis=1)
            df[f"Average_in_period_{i}"] = df[f"Total_in_period_{i}"] / len(cols)
    
        return df, total_group_columns, average_group_columns
    
    # Usage: unpack all three returned values
    df, total_group_columns, average_group_columns = add_total_period_columns(consumer_load_norm_csv, column_groups, T)
    
    monthly_consumption = df.groupby("Consumer No")[total_group_columns].sum().reset_index()
    
    monthly_consumption['monthly_consumption'] = monthly_consumption[total_group_columns].sum(axis=1)
    
    df["monthly_consumption"] = df["Consumer No"].map(monthly_consumption.set_index("Consumer No")["monthly_consumption"])
    
    # Group by 'consumer_no' and calculate mean for average columns
    grouped_df = df.groupby("Consumer No")[average_group_columns].mean().reset_index()
    
    consumer_load_norm = grouped_df.iloc[:, -T:].values
    
    consumer_load_time_block_order =  grouped_df.drop(["Consumer No"], axis=1).columns
    
    L_C =[len(merged_ranges[timeblock]) for timeblock in range(T)]
    
    
    # Define bins and labels for total monthly consumption
    bins = [0, 120, 240, float('inf')]
    labels = ['0-120', '120-240', '240+']
    
    # Create a new column for the bins
    if ('consumption_bin' in df.columns) == False:
        df['consumption_bin'] = pd.cut(
            df['monthly_consumption'],
            bins=bins,
            labels=labels,
            right=False
        )
    
    
    # Read bins
    peak_price_hours =pd.read_excel(f"{model_input_file}", sheet_name= "peak_price_hours")  # Your file with cutoffs
    
    total_blocks = peak_price_hours['Peak_Hour'].max()
    cutoffs = peak_price_hours['Peak_Hour'].values
    
    # Initialize start of first bin
    start = peak_price_hours['Peak_Hour'].min()
    bins = []
    
    for cutoff in cutoffs:
        bins.append((start, int(cutoff)))
        start = int(cutoff) + 1
    
    # Create Python ranges
    peak_range = [range(s, e + 1) for s, e in bins]
    
    elasticity_estimate =pd.read_excel(f"{model_input_file}", sheet_name= "elasticity_settings")  # Your file with cutoffs
    
    sp_unit_norm_cost_org = pd.read_excel(f"{model_input_file}", sheet_name="market_price_forecast")
    
    
    sp_unit_norm_cost_org = sp_unit_norm_cost_org[["forecast"]].values
    
    sp_unit_norm_cost_org = sp_unit_norm_cost_org.flatten()
    
    sp_unit_norm_cost = np.zeros((scenarios, len(sp_unit_norm_cost_org)))
    
    sp_unit_norm_cost[0, :] = sp_unit_norm_cost_org/1000 
    
    for scenario in range(1, scenarios):
        std_dev = abs(np.random.normal(0, std_dev_market_prices))  # Ensure std_dev is non-negative
        sp_unit_norm_cost[scenario, :] = sp_unit_norm_cost[0, :] + np.random.normal(0, std_dev, size=sp_unit_norm_cost_org.shape)
    
    
    sp_unit_norm_cost = np.where(sp_unit_norm_cost < 0, 0.01, sp_unit_norm_cost)
    sp_unit_norm_cost = np.where(sp_unit_norm_cost > 10, 10, sp_unit_norm_cost)
    
    
    R = sp_unit_norm_cost.shape[1]
    
    
    def create_membership_matrix(merged_ranges, sp_total_blocks, column_heads):
        """
        Create a binary matrix of shape (T, R),
        where T = number of merged ranges,
        R = total number of time blocks,
        matrix[t, r] = 1 if r in merged_ranges[t], else 0.
    
        Args:
            merged_ranges: list of range objects or lists defining each bin.
            total_blocks: int, total number of time blocks (R).
    
        Returns:
            numpy.ndarray: binary matrix (T x R)
        """
    
        total_columns = 0
        for group in column_heads:
            total_columns += len(group)
        
        T = len(merged_ranges)
        R = total_columns
        matrix = np.zeros((T, R), dtype=int)
    
        for t, time_range in enumerate(merged_ranges):
            for r in range(R):
                # Time blocks are often 1-based, adjust if your ranges and indexing differ
                # Here assuming time blocks start at 1, and matrix columns index at 0
                time_block = r + 1
                if time_block in time_range:
                    matrix[t, r] = 1
    
        return matrix
    
    
    membership_matrix = create_membership_matrix(merged_ranges, total_blocks,column_groups)
    print(membership_matrix)
    
    
    ## DEFINE THE VARIABLES
    
    u_auxiliary = model.addVars(scenarios, vtype=GRB.CONTINUOUS, lb = cvar_auxiliary_lower_limit, ub = cvar_auxiliary_upper_limit, name="u_auxiliary")
    delta_lambda = model.addVars(J, T, lb = lower_limit_to_change_allowed,  ub = upper_limit_to_change_allowed,  vtype=GRB.CONTINUOUS, name="delta_lambda")
    value_at_risk = model.addVar(vtype=GRB.CONTINUOUS, lb= var_lower_limit,ub = var_upper_limit, name="value_at_risk")
    
    
    # DEFINE THE PARAMETERS
    
    lambda_C = np.ones((J,T))  # energy price in respective time slots
    elasticity = np.ones((J,T,W))  #Elasticity of the consumer j in period t in scenario w
    lambda_P = sp_unit_norm_cost.T # pool price for period R and scenario w
    
    
    elasticity = consumer_load_norm_csv[['Consumer No', 'Category']].drop_duplicates()
    
    
    # Clean the Category column to be lowercase and remove spaces
    elasticity['Category'] = elasticity['Category'].str.lower().str.replace(' ', '')
    elasticity_estimate['category_name'] = elasticity_estimate['category_name'].str.lower().str.replace(' ', '')
    
    # Create mapping dictionaries
    elasticity_estimate_map = elasticity_estimate.set_index('category_name')['category_elasticity'].to_dict()
    
    # Apply mapping
    elasticity['elasticity'] = elasticity['Category'].map(elasticity_estimate_map)
    
    elasticity_matrix = np.tile(elasticity['elasticity'].values[:, np.newaxis, np.newaxis], (1, T, W))
    elasticity_matrix.shape
    
    lambda_C_assam = df[['Consumer No', 'Category',"consumption_bin"]].drop_duplicates()
    
    
    lambda_C_assam = lambda_C_assam[["Category", "consumption_bin"]]
    
    # Clean the Category column to be lowercase and remove spaces
    lambda_C_assam['Category'] = lambda_C_assam['Category'].str.lower().str.replace(' ', '')
    tariff_data['category_name'] = tariff_data['category_name'].str.lower().str.replace(' ', '')
    
    dom_a_bin_tariff = lambda_C_assam[lambda_C_assam['Category'] == "doma"]
    
    dom_a_bin_tariff.shape
    
    # Filter for DOM A rows in tariff_data
    dom_a_mask = lambda_C_assam['Category'] == 'doma'
    
    if dom_a_bin_tariff.shape[0] != 0:
        # Create a mapping from consumption_bin to average_energy_tariff for DOM A
        dom_a_bin_tariff_map = dom_a_bin_tariff.set_index('consumption_bin')['average_energy_tariff'].to_dict()
        # Update the 'Revised Energy Charges (Rs/kWh)' column for DOM A rows using the mapping
        lambda_C_assam.loc[dom_a_mask, 'Revised_Energy_Charges'] = lambda_C_assam.loc[dom_a_mask, 'consumption_bin'].map(dom_a_bin_tariff_map)
        # Display the updated rows for verification
    
    
    # Create mapping dictionaries
    fixed_charge_map = tariff_data.set_index('category_name')['Revised Fixed Charges (Rs/kW/mth or Rs/kVA/mth)'].to_dict()
    energy_charge_map = tariff_data.set_index('category_name')['Revised Energy Charges (Rs/kWh)'].to_dict()
    
    # Apply mapping
    lambda_C_assam['Revised_Fixed_Charges'] = lambda_C_assam['Category'].map(fixed_charge_map)
    lambda_C_assam['Revised_Energy_Charges'] = lambda_C_assam['Category'].map(energy_charge_map)
    
    
    
    lambda_C_array = np.tile(lambda_C_assam['Revised_Energy_Charges'].values, (T, 1)).T
    lambda_C = lambda_C_array
    
    
    # Step 2: Generate vector v from normal distribution
    v = np.random.normal(loc=0.0, scale=std_dev_elasticity, size=N)
    
    # Step 3: Create a 3D array of shape (J, T, N)
    # Step 4: Broadcast v to shape (J, T, N)
    result = np.tile(v, (J, T, 1))  # shape will be (J, T, N)
    
    
    ## Create Stochastic Elasticity
    elasticity = elasticity_matrix + result
    
    
    consumer_category = (
        consumer_load_norm_csv['Consumer No'].unique()
    )
    
    
    consumer_load = consumer_load_norm
    
    # # Plotting
    # plt.figure(figsize=(14, 6))
    # for consumer in range(consumer_load_norm.shape[0]):
    #     plt.plot(consumer_load_norm[consumer, :], label=f"Consumer {consumer_category[consumer]}", linewidth=2, linestyle='--')
    
    # plt.xlabel("Time Blocks")
    # plt.xticks(range(T))
    # plt.ylabel("Units consumed (kWh)")
    # plt.title("Consumer Load Profiles")
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)  # Legend at the bottom
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()
    
    
    # plt.figure(figsize=(14, 6))
    # for scenario in range(scenarios):
    #     plt.plot(sp_unit_norm_cost[scenario,:], linewidth=2, linestyle ="--")
    # #plt.plot(fc_unit_cost, label='Forward Contract Price', linestyle= '--', color= 'black')
    # plt.xlabel("Time Blocks")
    # plt.ylabel("Unit Cost (Rs/MWh)")
    # plt.title("Unit Norm Cost Profiles with High Price Variability in Non-Solar Hours")
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()
    
    
    
    if run_CVar_model == 1:
        # Equation_9
        model_objective = value_at_risk  - ( 1/ (1- alpha))*gp.quicksum( probability[scenario]*u_auxiliary[scenario] for scenario in range(scenarios))
    
        # Equation_15
    
        # RHS : First term
        # value_at_risk
    
        # RHS : Second term
        # gp.quicksum( consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock] for consumer in range(J) for timeblock in range(T) )
    
        # RHS : Third term
        # gp.quicksum( elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock] for consumer in range(J) for timeblock in range(T) )
    
        # RHS : Fourth term
        # gp.quicksum( (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock]*delta_lambda[consumer,timeblock]) for consumer in range(J) for timeblock in range(T) )
    
        # RHS : Fifth term
        # gp.quicksum( (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock]*lambda_P[timeblock,consumer]) for consumer in range(J) for timeblock in range(T) )
    
        model.addConstrs( ( u_auxiliary[scenario]
                        >=
                        value_at_risk
                        - gp.quicksum( consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock] for consumer in range(J) for timeblock in range(T) )
                        + gp.quicksum( elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock] for consumer in range(J) for timeblock in range(T) )
                        + gp.quicksum( (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock]*delta_lambda[consumer,timeblock]) for consumer in range(J) for timeblock in range(T) )
                        - gp.quicksum( (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*membership_matrix[timeblock,sp_timeblock]*delta_lambda[consumer,timeblock]*lambda_P[sp_timeblock,scenario]) for consumer in range(J) for sp_timeblock in range(R) for timeblock in range(T) )
                        for scenario in range(scenarios) )
                        , name= "Equation_15_w" )
    
        model.update()
    
        model.setObjective(model_objective, GRB.MAXIMIZE)
    
    else:
        # Calculate the change in profit
    
        term_1 = gp.quicksum(probability[scenario]*( 1 - elasticity[consumer,timeblock,scenario])*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock] for scenario in range(scenarios) for timeblock in range(T) for consumer in range(J))
        term_2 = gp.quicksum( (1/lambda_C[consumer,timeblock])*probability[scenario]*elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock]*delta_lambda[consumer,timeblock] for scenario in range(scenarios) for timeblock in range(T) for consumer in range(J) )
        term_3 = gp.quicksum( (1/lambda_C[consumer,timeblock])*probability[scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*sp_unit_norm_cost[scenario,timeblock]*delta_lambda[consumer,timeblock] for scenario in range(scenarios) for timeblock in range(T) for consumer in range(J) )
    
        expected_profit = term_1 - term_2 + term_3
    
        model.setObjective(expected_profit, GRB.MAXIMIZE)
    
    
    
    # Equation_10
    # Energy consumed by each consumer in a day cannot be modified
    # Only load shifting within time periods in a day is allowed
    
    # NOTE. Haven't inserted any L_t_C term in this equation yet. 
    # ---> UPDATE: ADDED L_C now
    
    # P_t_C = consumer_load[consumer,timeblock]
    
    model.addConstrs( ( - gp.quicksum( (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock]) for timeblock in range(T) ) 
                       == 
                       0 for consumer in range(J) for scenario in range(scenarios) ) 
                     , name = "Equation_10_j_w" )
    
    model.update()
    
    
    # Equation_11
    # Payments of each consumer cannot increase
    
    # NOTE. Haven't inserted any L_t_C term in this equation yet.  
    # --.>>> Now, *L_C[timeblock] modification made
    
    # RHS
    # gp.quicksum( consumer_load[consumer,timeblock]*lambda_C[consumer,timeblock] for timeblock in range(T) )
    
    # LHS : Second term
    # gp.quicksum( consumer_load[consumer,timeblock]*( lambda_C[consumer,timeblock] + delta_lambda[consumer,timeblock]) for timeblock in range(T) )
    
    # LHS : First term
    # gp.quicksum( (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock])*( lambda_C[consumer,timeblock] + delta_lambda[consumer,timeblock]) for timeblock in range(T) )
    
    model.addConstrs( (gp.quicksum( (1/(lambda_C[consumer,timeblock]))*L_C[timeblock]*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock])*( lambda_C[consumer,timeblock] + delta_lambda[consumer,timeblock]) for timeblock in range(T) )
                       - gp.quicksum( consumer_load[consumer,timeblock]*L_C[timeblock]*( lambda_C[consumer,timeblock] + delta_lambda[consumer,timeblock]) for timeblock in range(T) )
                       -  gp.quicksum( consumer_load[consumer,timeblock]*L_C[timeblock]*lambda_C[consumer,timeblock] for timeblock in range(T) )
                       <=
                       0
                       for consumer in range(J) for scenario in range(scenarios) ),
                       name = "Equation_11_j_w" )
    
    model.update()
    
    
    # Equation_12
    
    # Tariffs after modification cannot be negative
    
    model.addConstrs( ( lambda_C[consumer,timeblock] + delta_lambda[consumer,timeblock] 
                       >=
                       lower_limit_tariff
                       for consumer in range(J) for timeblock in range(T) 
                       ), 
                       name = "Equation_12_j_w" )
    
    model.update()
    
    
    
    # Equation_13
    
    # Power consumer by each consumer after load-shifting cannot be negative
    
    
    model.addConstrs( ( consumer_load[consumer,timeblock] 
                       -
                       (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock])
                       >=
                       min_power_consumer_after_load_shifting
                       for consumer in range(J)
                       for timeblock in range(T)
                       for scenario in range(scenarios) 
                       )
                       ,name = "Equation_13_j_t_w" )
    
    model.update()
    
    
    # Equation_14
    
    # Demand ramping constraint - Lower Limit
    
    model.addConstrs( ( - demand_ramp*consumer_load[consumer,timeblock] 
                       <= 
                       - (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock])
                       for consumer in range(J)
                       for timeblock in range(T)
                       for scenario in range(scenarios) 
                       )
                       ,name = "Equation_14_lower_limit_j_t_w" )
    
    # Demand ramping constraint - Upper Limit
                       
    model.addConstrs( ( - (1/(lambda_C[consumer,timeblock]))*(elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*delta_lambda[consumer,timeblock])
                       <=
                       demand_ramp*consumer_load[consumer,timeblock] 
                       for consumer in range(J)
                       for timeblock in range(T)
                       for scenario in range(scenarios) 
                       )
                       ,name = "Equation_14_upper_limit_j_t_w" )
    
    model.update()
                                          
    
    model.printStats()
    
    
    model.setParam("LogFile", "SM_model_t2.log")
    model.setParam('PreDual', 1)
    model.setParam('Seed', 42)                # Set a fixed random seed
    model.setParam('Threads', 1)    
    
    
    #Include any .log file with the solver output
    model.write("SM_model_t2.mps")
    
    model.optimize()
    
    
    # Calculate the change in profit
    
    term_1 = gp.quicksum(probability[scenario]*( 1 - elasticity[consumer,timeblock,scenario])*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock] for scenario in range(scenarios) for timeblock in range(T) for consumer in range(J)).getValue()
    
    term_2 = gp.quicksum( (1/lambda_C[consumer,timeblock])*probability[scenario]*elasticity[consumer,timeblock,scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*delta_lambda[consumer,timeblock]*delta_lambda[consumer,timeblock] for scenario in range(scenarios) for timeblock in range(T) for consumer in range(J) ).getValue()
    
    term_3 = gp.quicksum( (1/lambda_C[consumer,timeblock])*probability[scenario]*consumer_load[consumer,timeblock]*L_C[timeblock]*sp_unit_norm_cost[scenario,timeblock]*delta_lambda[consumer,timeblock] for scenario in range(scenarios) for timeblock in range(T) for consumer in range(J) ).getValue()
    
    change_in_profit = term_1 - term_2 + term_3
    
    consumer_number_series = pd.Series(consumer_load_norm_csv['Consumer No'].unique())
    
    consumer_number_series
    
    
    # Extract tou_timeblock_tariff values into a DataFrame with dimensions (J x T)
    # Create the DataFrame
    delta_lambda_df = pd.DataFrame(
        #[[ round(delta_lambda[j, t].X/(L_C[t]),5) for t in range(T)] for j in range(J)],  ### Should this be divided by per period hour
        [[ round(delta_lambda[j, t].X,5) for t in range(T)] for j in range(J)],
        columns=[f"Period_{t}" for t in range(T)]
    )
    
    delta_lambda_df.insert(0, 'Consumer No', consumer_number_series)
    
    
    
    # Extract tou_timeblock_tariff values into a DataFrame with dimensions (J x T)
    # Create the DataFrame
    modified_lambda_df = pd.DataFrame(
        [[round(delta_lambda[j, t].X, 5) + lambda_C[j, t] for t in range(T)] for j in range(J)],
        columns=[f"Period_{t}" for t in range(T)]
    )
    
    modified_lambda_df.insert(0, 'Consumer No', consumer_number_series)
    
    modified_lambda_df['Consumer No'] = modified_lambda_df['Consumer No'].astype(str).replace(" ", "")
    
    
    
    # Extract fc_purchase values into a DataFrame
    value_at_risk_df = pd.DataFrame(
        [round(value_at_risk.X,10)],
        columns=[f"Risk_premium"],
    )
    
    
    
    # Extract fc_purchase values into a DataFrame
    u_auxiliary_df = pd.DataFrame(
        [round(u_auxiliary[scenario].X,2) for scenario in range(scenarios)],
        columns=[f"u_auxiliary"],
        index=[f"Scenario_{scenario}" for scenario in range(scenarios)]
    )
    
    consumer_demand_df = df
    
    
    consumer_demand_df['consumer_category_full'] = (
        consumer_demand_df['Category'].astype(str).str.upper().str.replace(" ", "") 
        + '|' +
        #consumer_demand_df['Sanctioned_Load_Group'].astype(str) + '|' +
        'Monthly_consumption_' + consumer_demand_df['consumption_bin'].astype(str) 
        #+ '|' +
        #'Cluster_' + consumer_demand_df['KMeans_Cluster'].astype('Int64').astype(str)
    )
    
    
    
    modified_lambda_df
    
    
    # Merge on "Consumer No" to bring Period_1 to Period_T columns
    
    if "Period_0" not in consumer_demand_df.columns:
        
        consumer_demand_df['Consumer No'] = consumer_demand_df['Consumer No'].astype(str).replace(" ", "")
    
        consumer_demand_df = consumer_demand_df.merge(
            modified_lambda_df[["Consumer No"] + [f"Period_{i}" for i in range(T)]],
            on="Consumer No",
            how="left"
        )
    
    
    
    elasticity_estimate
    
    
    
    consumption_df = consumer_demand_df
    
    # Step 1: Normalize the Category column in consumption_df
    consumption_df['Category_normalized'] = (
        consumption_df['Category'].str.lower().str.replace(" ", "", regex=False)
    )
    
    
    # Step 1: Normalize Category in lambda_C_assam
    lambda_C_assam['Category_normalized'] = (
        lambda_C_assam['Category'].str.lower().str.replace(" ", "", regex=False)
    )
    
    # Step 2: Create the maps
    energy_charge_map = dict(
        zip(lambda_C_assam['Category_normalized'], lambda_C_assam['Revised_Energy_Charges'])
    )
    
    fixed_charge_map = dict(
        zip(lambda_C_assam['Category_normalized'], lambda_C_assam['Revised_Fixed_Charges'])
    )
    
    
    # Apply maps
    consumption_df['energy_charge'] = consumption_df['Category_normalized'].map(energy_charge_map)
    consumption_df['fixed_charge'] = consumption_df['Category_normalized'].map(fixed_charge_map)
    
    
    # Step 3: Map elasticity values
    consumption_df['elasticity'] = consumption_df['Category_normalized'].map(elasticity_estimate_map)
    
    # Optional: Drop the helper column if not needed
    consumption_df.drop(columns=['Category_normalized'], inplace=True)
    
    
    # Ensure merged_ranges is a list of lists
    flattened_ranges = []
    for r in merged_ranges:
        flattened_ranges.append(list(r))  # force range objects to list
    
    # Loop through each period and its range
    for period_index, hours in enumerate(flattened_ranges):
        for hour in hours:
            original_col = f"Consumption_Hr_{hour}"
            modified_col = f"modified_Consumption_Hr_{hour}"
            period_col = f"Period_{period_index}"
    
            # Multiply the original demand by the period factor using row-wise alignment
            consumption_df[modified_col] = (
                consumption_df[original_col] - ( (consumption_df['elasticity']*consumption_df[original_col]*(consumption_df[period_col] - consumption_df['energy_charge']) )/consumption_df['energy_charge'] )
            )
    
    
    import pandas as pd
    
    # Step 1: Identify original and modified hourly columns
    consumption_cols = [col for col in consumption_df.columns if col.startswith("Consumption_Hr_")]
    modified_cols = [col for col in consumption_df.columns if col.startswith("modified_Consumption_Hr_")]
    
    # Step 2: Group by Consumer No and compute mean
    mean_consumption = consumption_df.groupby("Consumer No")[consumption_cols].mean()
    mean_modified = consumption_df.groupby("Consumer No")[modified_cols].mean()
    
    # Step 3: Rename columns to unified 'Hour_X' format
    mean_consumption.columns = [f"Hour_{col.split('_')[-1]}" for col in mean_consumption.columns]
    mean_modified.columns = [f"Hour_{col.split('_')[-1]}" for col in mean_modified.columns]
    
    # Step 4: Add 'Type' column
    mean_consumption['Type'] = 'Original'
    mean_modified['Type'] = 'Modified'
    
    # Step 5: Reset index to bring 'Consumer No' back as a column
    mean_consumption = mean_consumption.reset_index()
    mean_modified = mean_modified.reset_index()
    
    # Step 6: Combine both DataFrames
    combined_df = pd.concat([mean_consumption, mean_modified], ignore_index=True)
    
    # Step 7: Reorder columns to match the desired format
    hour_cols = sorted([col for col in combined_df.columns if col.startswith("Hour_")], key=lambda x: int(x.split('_')[1]))
    combined_df = combined_df[['Consumer No', 'Type'] + hour_cols]
    
    
    combined_df
    
    # Write both dataframes into separate sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        modified_lambda_df.to_excel(writer, sheet_name="Modified_Lambda", index=False)
        delta_lambda_df.to_excel(writer, sheet_name="Delta_Lambda", index=False)
        combined_df.to_excel(writer, sheet_name="updated_profile_average", index=False)

