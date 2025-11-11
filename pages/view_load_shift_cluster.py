import dash
from dash import dcc, html
from dash import dcc, html, Input, Output, State, no_update
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from pages.cache import SaveDirCache , OutputFileNameCache
import os
import io
import pandas as pd


layout = html.Div([

    html.H1("Optariff: Cluster Model Results", style={"textAlign": "center", "marginBottom": "30px"}),
    dcc.Store(id = "cluster-output-json", data = {}),
    dcc.Input(id='dummy-upload', style={"display": "none"}),
    # Tabs
    dcc.Tabs(id='view-results-tabs1', value='', children=[
        dcc.Tab(label='Consumer', value='tab-consumer'),
        dcc.Tab(label='Cluster', value='tab-cluster'),
        dcc.Tab(label='Total', value='tab-total'),
    ]),

    # This part will update dropdowns depending on active tab
    html.Div(id='view-results-dropdown-area1', children=[], style={'margin': '20px 0'}),

    # Graph area
    html.Div(
        dcc.Graph(
            id='view-results-graph1',
            config={'responsive': True},
            style={'height': '80vh', 'width': '90%', 'margin': '0 auto'}
        )
    ),

    html.Div(id='view-results-loading-warning1', style={'color': 'red', 'marginTop': '10px'})

], style={'padding': '20px'})





def register_callbacks(app):

    @app.callback(
        Output("cluster-output-json","data"),
        Input("dummy-upload", "id")
    )

    ############################################# PLEASE TREAT ###############################################################################
    def read_data(dummy):
        #path = r"C:\Users\Varun Mehta\Desktop\Time_Of_Use\testing_graphs\test1234.xlsx"

        save_directory = SaveDirCache.get()
        output_file_name_str = OutputFileNameCache.get()  # Store in cache

        #print("in load shift populating consumer no")
        if not save_directory:
            # must return here, otherwise code will keep going
            return no_update, "No Save Dir Exists"

        #output_file_path = os.path.join(save_directory, "output_file.xlsx")
        output_file_path = os.path.join(save_directory, f"{output_file_name_str}.xlsx")

        if not os.path.exists(output_file_path):
            return [], f"Save dir is {save_directory} — waiting for output to be generated"

    
        # Load all sheets into a dict of DataFrames
        excel_data = pd.read_excel(output_file_path, sheet_name=None)

        # Convert each sheet's DataFrame to JSON (orient='split' for easy reconstruction)
        json_data = {sheet: df.to_json(date_format='iso', orient='split')
                     for sheet, df in excel_data.items()}

        return json_data

    ############################################# PLEASE TREAT ###############################################################################

    @app.callback(
        Output('view-results-dropdown-area1', 'children'),
        Input('view-results-tabs1', 'value')
    )
    def update_dropdown_area(selected_tab):
        if selected_tab == 'tab-consumer':
            return [
                html.Label("Select Consumer"),
                dcc.Dropdown(id='consumer-dropdown1', placeholder="Select a Consumer", style={'width': '50%'})
            ]

        elif selected_tab == 'tab-cluster':
            return [
                # html.Label("Select Category"),
                # dcc.Dropdown(id='category-dropdown1', placeholder="Select Category", style={'width': '50%'}),

                # html.Label("Select Sanctioned Load Bin"),
                # dcc.Dropdown(id='load-bin-dropdown1', placeholder="Select Load Bin", style={'width': '50%'}),

                # html.Label("Select Consumption Bin"),
                # dcc.Dropdown(id='consumption-bin-dropdown1', placeholder="Select Consumption Bin", style={'width': '50%'}),

                # html.Label("Select Cluster"),
                # dcc.Dropdown(id='cluster-dropdown1', placeholder="Select Cluster", style={'width': '50%'})
                html.Div([

        html.Div([
            html.Label("Select Category"),
            dcc.Dropdown(id='category-dropdown1', placeholder="Select Category", style={'width': '100%'}),
        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Sanctioned Load Bin"),
            dcc.Dropdown(id='load-bin-dropdown1', placeholder="Select Load Bin", style={'width': '100%'}),
        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Consumption Bin"),
            dcc.Dropdown(id='consumption-bin-dropdown1', placeholder="Select Consumption Bin", style={'width': '100%'}),
        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Cluster"),
            dcc.Dropdown(id='cluster-dropdown1', placeholder="Select Cluster", style={'width': '100%'}),
        ], style={'width': '23%', 'display': 'inline-block'}),

    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'marginBottom': '10px'})
            ]

        elif selected_tab == 'tab-total':
            return []  # No dropdowns

        return []


    @app.callback(
        Output('consumer-dropdown1', 'options'),
        Output('view-results-loading-warning1', 'children'),
        Input('consumer-dropdown1', 'id'), # dummy trigger
        State("cluster-output-json", "data")
    )
    def populate_cat(_, stored_data):

        try:
            sheet_df = pd.read_json(io.StringIO(stored_data['updated_profile_average']), orient = 'split')

        except Exception as e:
            return no_update, f"Error reading file: {e}"

        # just in case pandas returns None for some reason
        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [
            {'label': z, 'value': z}
            for z in sorted(sheet_df['Consumer No'].dropna().unique())
        ]
        return opts, ""


    @app.callback(

        Output("view-results-graph1", "figure", allow_duplicate=True),
        Input("view-results-tabs1", "value"),
        Input("consumer-dropdown1", "value"),
        State("cluster-output-json", "data"),
        prevent_initial_call=True
    )

    def plot_consumers(active_tab, consumer, stored_data):

        if stored_data is None:
            return go.Figure()

        try:
            output = pd.read_json(stored_data['updated_profile_average'], orient='split')
            tariff = pd.read_json(stored_data['updated_tariff'], orient='split')


        except Exception as e:
            return go.Figure()

        if active_tab == "tab-consumer":

            sub_original = output[(output['Consumer No'] == consumer) &
                                  (output['Type'] == "Before Optimization")
                # &
                # (output['Month'] == month)
                                  ]

            sub_mod = output[(output['Consumer No'] == consumer) &
                             (output['Type'] == "After Optimization")
                # &
                # (output['Month'] == month)
                             ]

            #net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
            net_save = output.loc[output['Consumer No'] == consumer, 'net_savings%']

            net_change_profit = output.loc[output['Consumer No'] == consumer,'Change_in_Retailer_Profit']

            if not net_save.empty:
                net_save_pct = round(net_save.iloc[0] , 2)
            else:
                net_save_pct = ""

            if not net_change_profit.empty:
                ncp = round(net_change_profit.values[0], 2)
            else:
                ncp = ""


            tcols = [f"Hour_{i}" for i in range(1, 25)]
            tariff_cols = [f"Tariff_{i}" for i in range(1, 25)]
            x_vals = list(range(1, 25))

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            for _, row in sub_original.iterrows():
                fig.add_trace(
                    go.Scatter(x=x_vals, y=row[tcols].tolist(), mode='lines',
                               name=f"Before Optimisation {row.get('Scenario', '')}", line=dict(color='blue')),
                    secondary_y=False
                )

            for _, row in sub_mod.iterrows():
                fig.add_trace(
                    go.Scatter(x=x_vals, y=row[tcols].tolist(), mode='lines',
                               name=f"After Optimisation {row.get('Scenario', '')}", line=dict(color='green')),
                    secondary_y=False
                )

            tariff_original = tariff[(tariff['Consumer No'] == consumer) & (tariff['Type'] == "Before Optimization")]
            tariff_opt = tariff[(tariff['Consumer No'] == consumer) & (tariff['Type'] == "After Optimization")]

            if not tariff_original.empty:
                row = tariff_original.iloc[0]
                fig.add_trace(
                    go.Bar(x=x_vals, y=[row[col] for col in tariff_cols],
                           name="Tariff Before Optimization", marker_color='rgba(0,0,255,0.3)', opacity=0.5),
                    secondary_y=True
                )

            if not tariff_opt.empty:
                row = tariff_opt.iloc[0]
                fig.add_trace(
                    go.Bar(x=x_vals, y=[row[col] for col in tariff_cols],
                           name="Tariff After Optimization", marker_color='rgba(0,128,0,0.3)', opacity=0.5),
                    secondary_y=True
                )

            fig.update_layout(
                title={'text': f"Load and Tariff Profiles for Consumer {consumer} | Savings : {net_save_pct} % ", # | Change in Retailer's Profit: ₹ {ncp}",
                       'font': dict(size=8)},
                xaxis_title='Hour of Day',
                yaxis_title='Load (kW)',
                autosize=True,
                # legend_title_text="Date",
                height=None,
                width=None,
                # legend_title='Legend',
                barmode='overlay',
                template='plotly_white',
                legend=dict(
                    orientation="h",  # horizontal legend
                    yanchor="top",
                    y=-0.2,  # push below the graph
                    xanchor="center",
                    x=0.5,
                    font=dict(size=9),  # smaller legend font
                    title=None  # remove "Legend" title
                )
            )

            fig.update_yaxes(title_text="Load (kW)", secondary_y=False)
            fig.update_yaxes(title_text="Tariff (₹/kWh)", secondary_y=True)
            fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

            return fig



    ############### Populate Category ################

    @app.callback(
        Output('category-dropdown1', 'options'),
        Output('load-bin-dropdown1', 'options'),
        Output('consumption-bin-dropdown1', 'options'),
        Output('cluster-dropdown1', 'options'),

        Input("view-results-tabs1", "value"),
        Input('category-dropdown1', 'value'),
        Input('load-bin-dropdown1', 'value'),
        Input('consumption-bin-dropdown1', 'value'),
        Input('cluster-dropdown1', 'value'),
        State('cluster-output-json', 'data')
    )
    def update_all_dropdowns(active_tab,category_val, load_bin_val, consumption_bin_val, cluster_val, stored_data):
        try:
            df = pd.read_json(io.StringIO(stored_data['updated_profile_average']), orient='split')
        except Exception as e:
            return no_update, no_update, no_update, no_update

        if df is None or df.empty:
            return [], [], [], []

        if active_tab == "tab-cluster":
            filtered_df = df.copy()
            # Apply filtering based on non-None selections
            if category_val:
                filtered_df = filtered_df[filtered_df['Category_col'] == category_val].copy()
            if load_bin_val:
                filtered_df = filtered_df[filtered_df['Loadbin_col'] == load_bin_val]
            if consumption_bin_val:
                filtered_df = filtered_df[filtered_df['Consumptionbin_col'] == consumption_bin_val]
            if cluster_val:
                filtered_df = filtered_df[df['Cluster_col'] == cluster_val]

            # Compute updated options based on filtered data
            cat_opts = [{'label': x, 'value': x} for x in sorted(filtered_df['Category_col'].dropna().unique())]
            load_opts = [{'label': x, 'value': x} for x in sorted(filtered_df['Loadbin_col'].dropna().unique())]
            cons_opts = [{'label': x, 'value': x} for x in sorted(filtered_df['Consumptionbin_col'].dropna().unique())]
            clust_opts = [{'label': x, 'value': x} for x in sorted(filtered_df['Cluster_col'].dropna().unique())]

            return cat_opts, load_opts, cons_opts, clust_opts

        else:
            return [], [], [], []

    @app.callback(

        Output("view-results-graph1", "figure", allow_duplicate=True),
        Input("view-results-tabs1", "value"),
        Input('category-dropdown1', 'value'),
        Input('load-bin-dropdown1', 'value'),
        Input('consumption-bin-dropdown1', 'value'),
        Input('cluster-dropdown1', 'value'),
        State("cluster-output-json", "data"),
        prevent_initial_call=True
    )

    def plot_category(active_tab, category, load_bin, consumption_bin, cluster, stored_data):


        if stored_data is None:
            return go.Figure()

        try:
            output = pd.read_json(stored_data['updated_profile_average'], orient='split')
            tariff = pd.read_json(stored_data['updated_tariff'], orient='split')


        except Exception as e:
            return go.Figure()

        if active_tab == "tab-cluster":

            sub_original = output[(output['Category_col'] == category) &
                                  (output['Loadbin_col'] == load_bin) &
                                  (output['Consumptionbin_col'] == consumption_bin) &
                                  (output['Cluster_col'] == cluster) &
                                  (output['Type'] == "Before Optimization")]


            sub_mod = output[(output['Category_col'] == category) &
                                  (output['Loadbin_col'] == load_bin) &
                                  (output['Consumptionbin_col'] == consumption_bin) &
                                  (output['Cluster_col'] == cluster) &
                                  (output['Type'] == "After Optimization")]


            try:
                net_savings_pct = round((sub_original['net_savings'].sum(axis = 0) / (sub_original['energy_bill'].sum(axis = 0) * 30)) * 100 , 2)
                net_change_profit = round(sub_original['Change_in_Retailer_Profit'].iloc[0] , 2)
            except:
                net_savings_pct = ""
                net_change_profit = ""

            tcols = [f"Hour_{i}" for i in range(1, 25)]
            tariff_cols = [f"Tariff_{i}" for i in range(1, 25)]
            x_vals = list(range(1, 25))


            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=sub_original[tcols].sum(axis=0),  # Sum across columns (row-wise)
                    mode='lines',
                    name='Before Optimisation (Total)',
                    line=dict(color='blue')
                ),
                secondary_y=False
            )

            # Plot summed values after optimization
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=sub_mod[tcols].sum(axis=0),  # Sum across columns (row-wise)
                    mode='lines',
                    name='After Optimisation (Total)',
                    line=dict(color='green')
                ),
                secondary_y=False
            )

            tariff_original = tariff[(tariff['Category_col'] == category) &
                                  (tariff['Loadbin_col'] == load_bin) &
                                  (tariff['Consumptionbin_col'] == consumption_bin) &
                                  (tariff['Cluster_col'] == cluster) &
                                  (tariff['Type'] == "Before Optimization")]

            tariff_opt = tariff[(tariff['Category_col'] == category) &
                                     (tariff['Loadbin_col'] == load_bin) &
                                     (tariff['Consumptionbin_col'] == consumption_bin) &
                                     (tariff['Cluster_col'] == cluster) &
                                     (tariff['Type'] == "After Optimization")]


            if not tariff_original.empty:
                row = tariff_original.iloc[0]
                fig.add_trace(
                    go.Bar(x=x_vals, y=[row[col] for col in tariff_cols],
                           name="Tariff Before Optimization", marker_color='rgba(0,0,255,0.3)', opacity=0.5),
                    secondary_y=True
                )

            if not tariff_opt.empty:
                row = tariff_opt.iloc[0]
                fig.add_trace(
                    go.Bar(x=x_vals, y=[row[col] for col in tariff_cols],
                           name="Tariff After Optimization", marker_color='rgba(0,128,0,0.3)', opacity=0.5),
                    secondary_y=True
                )

            fig.update_layout(
                 title={'text': f"Load and Tariff Profiles for Cluster {cluster} ", #| Savings %: {net_savings_pct},| Change in Retailer's Profit: ₹ {net_change_profit}",
                        'font': dict(size=8)},
                xaxis_title='Hour of Day',
                yaxis_title='Load (kW)',
                autosize=True,
                # legend_title_text="Date",
                height=None,
                width=None,
                # legend_title='Legend',
                barmode='overlay',
                template='plotly_white',
                legend=dict(
                    orientation="h",  # horizontal legend
                    yanchor="top",
                    y=-0.2,  # push below the graph
                    xanchor="center",
                    x=0.5,
                    font=dict(size=9),  # smaller legend font
                    title=None  # remove "Legend" title
                )
            )

            fig.update_yaxes(title_text="Load (kW)", secondary_y=False)
            fig.update_yaxes(title_text="Tariff (₹/kWh)", secondary_y=True)
            fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

            return fig


    @app.callback(

        Output("view-results-graph1", "figure", allow_duplicate=True),
        Input("view-results-tabs1", "value"),
        State("cluster-output-json", "data"),
        prevent_initial_call=True
    )

    def plot_total(active_tab, store_data):
        try:

            if active_tab == "tab-total":
                processing_df = pd.read_json(store_data["all_processing_df"], orient='split')
                sheet_df = pd.read_json(store_data['updated_profile_average'], orient = 'split')

                cols = [f'Hour_{i}' for i in range(1, 25)]
                before_opt = sheet_df[sheet_df['Type'] == 'Before Optimization'].copy()
                after_opt = sheet_df[sheet_df['Type'] == 'After Optimization'].copy()

                compare = {}
                for col in cols:
                    a = before_opt[col].sum()
                    b = after_opt[col].sum()
                    compare[col] = [a, b]

                # Convert to DataFrame for plotting
                compare_df = pd.DataFrame(compare, index=['Before Optimization', 'After Optimization']).T
                compare_df.reset_index(inplace=True)
                compare_df.rename(columns={'index': 'Hour'}, inplace=True)

                total_bill = processing_df['energy_bill'].sum(axis=0) * 30
                total_savings = processing_df['net_savings'].sum(axis=0)
                total_savings_pct = (total_savings / total_bill * 100).round(1)

                # Optional: Format Hour column to be numeric (Hour_1 → 1)
                compare_df['Hour'] = compare_df['Hour'].str.extract(r'Hour_(\d+)').astype(int)
                fig = go.Figure()

                fig.add_trace(go.Scatter(x=compare_df['Hour'], y=compare_df['Before Optimization'],
                                         name='Before Optimization', line=dict(color='blue'), mode='lines'))

                fig.add_trace(go.Scatter(x=compare_df['Hour'], y=compare_df['After Optimization'],
                                         name='After Optimization', line=dict(color='green'), mode='lines'))

                fig.update_layout(
                    title={'text': f"Load and Tariff Profiles for ALL consumers ", #,  | Total Savings %: {total_savings_pct} % ",
                           'font': dict(size=8)},
                    xaxis_title='Hour of Day',
                    yaxis_title='Total Load (kW)',
                    barmode='group',
                    autosize=True,
                    height=None,
                    width=None,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=9),
                                title=None)
                )
                fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
                return fig

        except Exception as e:
            return go.Figure()