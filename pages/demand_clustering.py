import os
#os.system('pip install -r requirements.txt')

#from sklearn_extra.cluster import KMedoids
#
from datetime import datetime
import kmedoids
import openpyxl
import os
import math
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

#output_path = r"C:\Users\Varun Mehta\Desktop\RepDays"
#data = pd.read_excel(r"C:\Users\Varun Mehta\Desktop\input_clustering 1.xlsx")





def plot_subplots(columns, data, variable, size_of_block, save_dir=None):
    """
    columns: list of 24 column names (e.g. ['d0', 'd1', ..., 'd23'])
    data: DataFrame with ['block_idx','Cluster','rep_day_flag','Date', ...columns]
    variable: one of {"Demand", "Solar", "Wind"} for y-axis labeling
    size_of_block: integer, number of days in each block
    save_dir: optional path; if provided, saves each block plot as JSON
    """
    y_labels = {
        "Demand": "Demand (MW)",
        "Solar":  "Solar CUF",
        "Wind":   "Wind CUF"
    }
    y_label = y_labels.get(variable, variable)

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    for block in sorted(data['block_idx'].unique()):
        sub_block = data[data['block_idx'] == block].copy()

        # date range
        dates = pd.to_datetime(sub_block['Date'])
        min_date = dates.min().strftime('%Y-%m-%d')
        max_date = dates.max().strftime('%Y-%m-%d')

        clusters = sorted(sub_block['Cluster'].unique())
        n = len(clusters)
        ncols = 2
        nrows = math.ceil(n / ncols)

        fig = make_subplots(rows=nrows, cols=ncols,
                            subplot_titles=[f"Cluster {c}" for c in clusters],
                            shared_xaxes=False, shared_yaxes=True)

        for i, cluster in enumerate(clusters):
            row = (i // ncols) + 1
            col = (i % ncols) + 1

            sub_df = sub_block[sub_block['Cluster'] == cluster]
            rep_df = sub_df[sub_df['rep_day_flag'] == 1]

            for _, rowdata in sub_df.iterrows():
                fig.add_trace(go.Scatter(
                    x=list(range(24)),
                    y=rowdata[columns],
                    mode='lines',
                    line=dict(color='lightblue', width=1),
                    opacity=0.6,
                    showlegend=False
                ), row=row, col=col)

            for _, rowdata in rep_df.iterrows():
                date_label = pd.to_datetime(rowdata['Date']).strftime('%Y-%m-%d')
                fig.add_trace(go.Scatter(
                    x=list(range(24)),
                    y=rowdata[columns],
                    mode='lines',
                    line=dict(color='red', width=2.5),
                    name=f"Rep Day: {date_label}",
                    showlegend=True
                ), row=row, col=col)

        fig.update_layout(
            height=300 * nrows,
            width=1000,
            title_text=f"{min_date} → {max_date}  |  Window: {size_of_block} days",
            title_x=0.5,
            margin=dict(t=80),
        )

        fig.update_xaxes(title_text="Hour of Day")
        fig.update_yaxes(title_text=y_label)

        # Save as JSON
        if save_dir:
            fname = f"Time_Window_{block+1:02d}.json"
            json_path = os.path.join(save_dir, fname)
            pio.write_json(fig, json_path, pretty=True)

        # optionally return the figure if needed for display
        # return fig



def read_input(file_path):
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0])
    df = df.fillna(0)
    return df


def n_day_clusters(data, n):
    df = data.copy(deep = True)
    try:
        df['block_idx'] = -1  # Initialize with -1 or NaN
        len_data = len(df)
        block_id = 0

        for i in range(0, len_data, n):
            #if i + n <= len_data:  # Only assign complete blocks
            end_idx = min(i+n, len_data)
            if end_idx == len_data:
                df.loc[i: end_idx -1, 'block_idx'] = block_id - 1
            else:
                df.loc[i: end_idx-1, 'block_idx'] = block_id

            block_id += 1

        return df

    except Exception as e:
        print(f"Error in n_day_clusters: {e}")
        return df

def identify_quarter(date, quarters):
    for quarter, (start, end) in quarters.items():
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        if start_date <= date <= end_date:
            return quarter
    return None


#df = n_day_clusters(data, 27)



def identify_representative_days(data, block_idx, n_clusters, fixed_date=None, distance_metric = 'euclidean', opt_flag = None):


    df = data.copy(deep = True)

    df_quarter = df[df['block_idx'] == block_idx].copy()
    df_quarter.reset_index(drop=True, inplace = True)

    num_day_for_clustering = len(df_quarter['block_idx'])

    if fixed_date:
        df_quarter = df_quarter[df_quarter['Date'] != fixed_date].copy()
        df_quarter.reset_index(drop = True, inplace = True)

    #demand_cols = [f"d{i}" for i in range(0,24)]
    input_columns = [col for col in df.columns if col != "Date" and "block_idx"]
    # Extract the specified features for clustering
    X = df_quarter[input_columns].values

    # Normalize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    dist_matrix = pairwise_distances(X_scaled, metric=distance_metric)

    fp = None
    if opt_flag == "No":

        fp = kmedoids.fasterpam(dist_matrix, n_clusters)

    elif opt_flag == "Yes":

        kmin, kmax = 1, num_day_for_clustering//3

        fp = kmedoids.dynmsc(dist_matrix, kmax, kmin)

    elif opt_flag is None:

        fp = kmedoids.fasterpam(dist_matrix, n_clusters)

    df_quarter['Cluster'] = fp.labels
    df_quarter['rep_day_flag'] = 0

    # Evaluate clustering quality
    silhouette_avg = silhouette_score(X_scaled, fp.labels)
    davies_bouldin = davies_bouldin_score(X_scaled, fp.labels)
    calinski_harabasz = calinski_harabasz_score(X_scaled, fp.labels)

    # print(f"Silhouette Score for {start_date} to {end_date} with metric {metric} - features {feature_set_name}: {silhouette_avg}")
    # print(f"Davies-Bouldin Index for {start_date} to {end_date} with metric {metric} - features {feature_set_name}: {davies_bouldin}")
    # print(f"Calinski-Harabasz Index for {start_date} to {end_date} with metric {metric} - features {feature_set_name}: {calinski_harabasz}")
    # print(f"-----------------------------------------------------------------------------------------")

    results_df = pd.DataFrame({
        # 'Feature Set': [feature_set_name],
        # 'Metric': [metric],
        #'Quarter': [q],
        #'Start Date': [start_date],
        #'End Date': [end_date],
        'Block_idx' : [block_idx],
        'Silhouette Score': [silhouette_avg],
        'Davies-Bouldin Index': [davies_bouldin],
        'Calinski-Harabasz Index': [calinski_harabasz]
    })

    # Find the representative days
    df_quarter['rep_day_flag'] = df_quarter.index.isin(fp.medoids).astype(int)
    representative_days = df_quarter.iloc[fp.medoids].copy()


    fixed_day = None

    if fixed_date:

        fixed_day = df[df['Date'] == fixed_date].copy()
        fixed_day['Cluster'] = n_clusters
        fixed_day['rep_day_flag'] = 1

        if opt_flag == "No" or opt_flag is None:
            fixed_day['Cluster'] = n_clusters  # Assign a new cluster label for the fixed date

        elif opt_flag == "Yes":
            n_clusters = len(df_quarter['Cluster'].unique())
            fixed_day['Cluster'] = n_clusters


        representative_days = pd.concat([representative_days, fixed_day])

    # Calculate the weightage of each cluster in number of days
    cluster_weightage = df_quarter['Cluster'].value_counts().sort_index()

    if fixed_date:
        additional_weight = pd.Series({n_clusters : 1})
        cluster_weightage = pd.concat([cluster_weightage, additional_weight])
        df_quarter = pd.concat([df_quarter, fixed_day])

    representative_days = representative_days.merge(cluster_weightage.rename('Weightage'), left_on='Cluster',
                                                    right_index=True)

    return representative_days, results_df, df_quarter




# Calculate the sum of energy*weightage for the representative days
def calculate_weighted_energy(representative_days):
    return (representative_days['energy'] * representative_days['Weightage']).sum()

def calculate_weighted_generation(representative_days, columns):
    return (representative_days[columns].sum(axis=1) * representative_days['Weightage']).sum()


def main(input_data, metric, n_block, normal_cluster_value, output_path, opt_flag):
    #data = pd.read_excel(input_path)
    data = input_data
    df = n_day_clusters(data, n_block)

    unique_blocks = df['block_idx'].unique()


    max_value = df['daily_max'].max()  # Find the maximum value in the 'daily_max' column
    max_index = df['daily_max'].idxmax()
    peak_block = df.loc[max_index, 'block_idx']

    normal_cluster = normal_cluster_value
    peak_cluster = normal_cluster - 1
    max_date_str = df[df['daily_max'] == max_value]['Date'].astype(str).iloc[0]

    """
    #
    #date_obj = datetime.strptime(max_date_str, '%Y-%m-%d')
    # peak_quarter = identify_quarter(date_obj, quarters)
    
    """
    """
    dwsn = [col for col in df.columns if
            col.startswith('d') or col.startswith('w') or col.startswith('s') or col.startswith(
                'n') or col == 'daily_max' or col == 'energy']
    dws = [col for col in df.columns if
           col.startswith('d') or col.startswith('w') or col.startswith('s') or col == 'daily_max' or col == 'energy']
    feature_sets = {'dwsn': dwsn, 'dws': dws} """

    results = {}
    scores = {}
    all_representative_days = []

    transformed_data = []


    #for q, dates in quarters.items():
    for block in unique_blocks:
        rep_days = None

        if block == peak_block:
            rep_days, score_df, df_quarter = identify_representative_days(data = df, block_idx = block,
                                                              n_clusters=peak_cluster, distance_metric= metric,
                                                              fixed_date = max_date_str, opt_flag = opt_flag)

        else:
            rep_days, score_df, df_quarter = identify_representative_days(data = df,
                                                              n_clusters=normal_cluster, distance_metric=metric,
                                                              fixed_date=None, block_idx = block, opt_flag = opt_flag)
        all_representative_days.append(rep_days)
        transformed_data.append(df_quarter)

    #results[f"{feature_set_name}_{metric}"] = all_representative_days
    #scores[f"{feature_set_name}_{metric}"] = all_scores


        results[block] = rep_days
        scores[block] = score_df

    total_energy_original = df['energy'].sum()
    solar_columns = [f's{i}' for i in range(24)]  # Define solar columns
    wind_columns = [f'w{i}' for i in range(24)]  # Define wind columns
    total_solar_original = df[solar_columns].sum().sum()
    total_wind_original = df[wind_columns].sum().sum()
    excel_output_file_path = os.path.join(output_path, "representative_days_and_weightages_cea.xlsx")

    all_rep_days = pd.concat(all_representative_days, axis = 0)
    transformed_original_data = pd.concat(transformed_data, axis = 0)

    all_rep_days.to_excel(os.path.join(output_path,"RepDays.xlsx"))
    transformed_original_data.to_excel(os.path.join(output_path, "Original_df_with_clusters.xlsx"))

    # 1. Define your hourly‐column lists
    demand_cols = [f"d{i}" for i in range(24)]
    wind_cols = [f"w{i}" for i in range(24)]
    solar_cols = [f"s{i}" for i in range(24)]

    # 2. Compute block size (assuming block 1 exists)
    size_of_block = len(transformed_original_data[transformed_original_data['block_idx'] == 1])

    # 3. Prepare an output folder


    # 4. Map each variable name to its columns
    variable_mapping = [
        ("Demand", demand_cols),
        ("Wind", wind_cols),
        ("Solar", solar_cols),
    ]

    plot_path = os.path.join(output_path, "Graphs")
    os.makedirs(plot_path, exist_ok= True)
    # 5. Loop and save
    for var_name, cols in variable_mapping:
        graphs_dir = os.path.join(plot_path, f"{var_name}")
        os.makedirs(graphs_dir, exist_ok=True)
        plot_subplots(
            columns=cols,
            data=transformed_original_data,
            variable=var_name,
            size_of_block=size_of_block,
            save_dir=graphs_dir
        )

    with pd.ExcelWriter(excel_output_file_path, engine='openpyxl') as writer:

        all_rep_days.to_excel(writer, sheet_name = "All_Rep_Days", index = False)
        # Perform the calculation for each feature set and metric combination
        for key, rep_days in results.items():
            weighted_energy_sum = calculate_weighted_energy(rep_days)
            weighted_solar_sum = calculate_weighted_generation(rep_days, solar_columns)
            weighted_wind_sum = calculate_weighted_generation(rep_days, wind_columns)

            energy_percentage_difference = f"{round(abs(total_energy_original - weighted_energy_sum) / total_energy_original * 100, 2)}%"
            solar_percentage_difference = f"{round(abs(total_solar_original - weighted_solar_sum) / total_solar_original * 100, 2)}%"
            wind_percentage_difference = f"{round(abs(total_wind_original - weighted_wind_sum) / total_wind_original * 100, 2)}%"

            # Create a DataFrame to hold the results
            df_results = pd.DataFrame({
                'Metric': ['Energy Difference Percentage',
                           'Solar Difference Percentage',
                           'Wind Difference Percentage'],
                'Value': [energy_percentage_difference,
                          solar_percentage_difference,
                          wind_percentage_difference]
            })

            # Write the DataFrame to a new sheet in the Excel file
            df_results.to_excel(writer, sheet_name=str(key) + '_energy_diff', index=False)
            rep_days.to_excel(writer, sheet_name=str(key) + '_rdays', index=False)
            if key in scores:
                df_scores = scores[key]
                df_scores.to_excel(writer, sheet_name=str(key) + '_score', index=False)

        print("Results are ready")

    return "Done"


#main(input_data = data, metric = "euclidean", n_block = 90, normal_cluster_value = 6, output_path = output_path, opt_flag = "No")



