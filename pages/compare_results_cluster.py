
import plotly.graph_objs as go
#from pages import run_model_dashboard
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate
from dash import Input, Output, State,  no_update
import plotly.graph_objects as go
import base64
import pandas as pd
import os
import io

from pages.cache import TimeBlockRangeCache, TimeBlockRangeCacheCompareLeft, TimeBlockRangeCacheCompareRight

import dash
from dash import dcc, html

layout = html.Div([

    html.H1("Optariff: Cluster Model Result Comparison", style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div([

        # Left Panel
        html.Div([

            html.H4("Upload Result (Dataset 1)"),

            dcc.Upload(
                id="cluster-upload-data-left",
                children=html.Div(["Drag and drop or ", html.A("select a file")]),
                style={
                    "width": "100%",
                    "height": "30px",
                    "lineHeight": "30px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "marginBottom": "10px",
                    "cursor": "pointer"
                },
                multiple=False
            ),

            dcc.Store(id="cluster-store-uploaded-file-left"),
            html.Div(id="cluster-file-upload-status-left", style={"fontSize": "12px", "color": "green"}),

            ##################################### LEFT TAB ######################################################

            dcc.Tabs(id='cluster-left-tabs', value='', children=[

                dcc.Tab(label='Total', value='cluster-total-left', children=[
                    #html.Div("No dropdowns required in Total tab.", style={'padding': '10px', 'fontStyle': 'italic'})
                ]),

                dcc.Tab(label='Cluster', value='tab-cluster', children = [

                    html.Div([

                        html.Div([
                            html.Label("Select Category", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='left-category-dropdown1', placeholder="Select Category",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

                        html.Div([
                            html.Label("Select Sanctioned Load Bin", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='left-load-bin-dropdown1', placeholder="Select Load Bin",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

                        html.Div([
                            html.Label("Select Consumption Bin", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='left-consumption-bin-dropdown1', placeholder="Select Consumption Bin",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

                        html.Div([
                            html.Label("Select Cluster", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='left-cluster-dropdown1', placeholder="Select Cluster", style={'width': '100%'}),
                        ], style={'width': '23%', 'display': 'inline-block'}),

                    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'marginBottom': '10px'})


                ]),

                dcc.Tab(label='Consumer', value='cluster-consumer-left', children=[
                    html.Div([
                        html.Label("Select Consumer", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='consumer-dropdown-left',
                            placeholder="Select a Consumer",
                            style={'width': '50%'}
                        ),
                    ], style={'padding': '10px'})
                ]),


            ]),

            dcc.Graph(
                id='cluster-load-graph-left',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),

            html.Div(id='cluster-load-comparison-loading-warning-left', style={'color': 'red'}),

            html.Div(id='cluster-logs-area-left', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})

        ], style={'width': '48%', 'padding': '20px'}),


##################################### RIGHT TAB ######################################################
        html.Div([

            html.H4("Upload Result (Dataset 2)"),

            dcc.Upload(
                id="cluster-upload-data-right",
                children=html.Div(["Drag and drop or ", html.A("select a file")]),
                style={
                    "width": "100%",
                    "height": "30px",
                    "lineHeight": "30px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "marginBottom": "10px",
                    "cursor": "pointer"
                },
                multiple=False
            ),

            dcc.Store(id="cluster-store-uploaded-file-right"),
            html.Div(id="cluster-file-upload-status-right", style={"fontSize": "12px", "color": "green"}),

            dcc.Tabs(id='cluster-right-tabs', value='', children=[

            dcc.Tab(label='Total', value='cluster-total-right', children=[
                    #html.Div("No dropdowns required in Total tab.", style={'padding': '10px', 'fontStyle': 'italic'})
                ]),

                dcc.Tab(label='Cluster', value='tab-cluster', children = [

                    html.Div([

                        html.Div([
                            html.Label("Select Category", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='right-category-dropdown1', placeholder="Select Category",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

                        html.Div([
                            html.Label("Select Sanctioned Load Bin", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='right-load-bin-dropdown1', placeholder="Select Load Bin",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

                        html.Div([
                            html.Label("Select Consumption Bin", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='right-consumption-bin-dropdown1', placeholder="Select Consumption Bin",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

                        html.Div([
                            html.Label("Select Cluster", style={'fontSize': '10px'}),
                            dcc.Dropdown(id='right-cluster-dropdown1', placeholder="Select Cluster",
                                         style={'width': '100%'}),
                        ], style={'width': '23%', 'display': 'inline-block'}),

                    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'marginBottom': '10px'})

                ]),

                dcc.Tab(label='Consumer', value='cluster-consumer-right', children=[
                    html.Div([
                        html.Label("Select Consumer", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='consumer-dropdown-right',
                            placeholder="Select a Consumer",
                            style={'width': '50%'}
                        ),
                    ], style={'padding': '10px'})
                ]),

                ]),

            dcc.Graph(
                id='cluster-load-graph-right',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),

            html.Div(id='cluster-load-comparison-loading-warning-right', style={'color': 'red'}),

            html.Div(id='cluster-logs-area-right', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})

        ], style={'width': '48%', 'padding': '20px'})

    ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '4%'})

], style={'padding': '20px'})



############################## CALLBACKS #################################################

def register_callbacks(app):


    #############################
    ####### STEP 1 ############## READ INPUT FILE - LEFT
    ############################# 

    @app.callback(
        Output("cluster-store-uploaded-file-left", "data"),
        Output("cluster-file-upload-status-left", "children"),
        Output("cluster-logs-area-left", "children", allow_duplicate=True),
        Input("cluster-upload-data-left", "contents"),
        State("cluster-upload-data-left", "filename"),
        prevent_initial_call=True,
    )
    def handle_file_upload_left(contents, filename):
        if not contents:
            raise PreventUpdate

        try:
            # Decode content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            buffer = io.BytesIO(decoded)

            # Load all sheets into a dict of DataFrames
            excel_data = pd.read_excel(buffer, sheet_name=None)

            # Convert each sheet's DataFrame to JSON (orient='split' for easy reconstruction)
            json_data = {sheet: df.to_json(date_format='iso', orient='split')
                         for sheet, df in excel_data.items()}

            return (
                json_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} stored to (LEFT)")
            )

        except Exception as e:
            return (
                no_update,
                html.Div("❌ Upload failed."),
                html.Div(f"❌ Error: {str(e)}")
            )

    ####################################
    ### UPLOAD FOR RIGHT PANEL
    ####################################

    @app.callback(
        Output("cluster-store-uploaded-file-right", "data"),
        Output("cluster-file-upload-status-right", "children"),
        Output("cluster-logs-area-right", "children", allow_duplicate=True),
        Input("cluster-upload-data-right", "contents"),
        State("cluster-upload-data-right", "filename"),
        prevent_initial_call=True,
    )
    def handle_file_upload_right(contents, filename):
        if not contents:
            raise PreventUpdate

        try:
            # Decode content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            buffer = io.BytesIO(decoded)

            # Load all sheets into a dict of DataFrames
            excel_data = pd.read_excel(buffer, sheet_name=None)

            # Convert each sheet's DataFrame to JSON (orient='split' for easy reconstruction)
            json_data = {sheet: df.to_json(date_format='iso', orient='split')
                         for sheet, df in excel_data.items()}

            return (
                json_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} stored (RIGHT)")
            )

        except Exception as e:
            return (
                no_update,
                html.Div("❌ Upload failed."),
                html.Div(f"❌ Error: {str(e)}")
            )


    ######

    @app.callback(
        Output("consumer-dropdown-left", "options"),
        Output("cluster-load-comparison-loading-warning-left", "children"),
        Input("cluster-store-uploaded-file-left", "data"),
        prevent_initial_call=True
    )
    def populate_consumer_dropdown_left(store_data):
        if not store_data:
            return no_update, "No file uploaded."

        sheet_df = pd.read_json(store_data["updated_profile_average"], orient='split')

        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Consumer No'].dropna().unique())]
        return opts, ""

    ######################### Populate LEFT Category #####################################################

    @app.callback(
        Output('left-category-dropdown1', 'options'),
        Output('left-load-bin-dropdown1', 'options'),
        Output('left-consumption-bin-dropdown1', 'options'),
        Output('left-cluster-dropdown1', 'options'),

        Input("cluster-left-tabs", "value"),
        Input('left-category-dropdown1', 'value'),
        Input('left-load-bin-dropdown1', 'value'),
        Input('left-consumption-bin-dropdown1', 'value'),
        Input('left-cluster-dropdown1', 'value'),
        Input('cluster-store-uploaded-file-left', 'data')
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

        Output("cluster-load-graph-left", "figure", allow_duplicate=True),
        Input("cluster-left-tabs", "value"),
        Input('left-category-dropdown1', 'value'),
        Input('left-load-bin-dropdown1', 'value'),
        Input('left-consumption-bin-dropdown1', 'value'),
        Input('left-cluster-dropdown1', 'value'),
        State("cluster-store-uploaded-file-left", "data"),
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

            tb_range = TimeBlockRangeCache.get()

            if tb_range["first"] is None or tb_range["last"] is None:
                # detect existing TB columns from dataset
                tcols = sorted([col for col in sub_original.columns if col.startswith("TB_")],
                               key=lambda c: int(c.split("_")[1]))
                x_vals = list(range(1, len(tcols) + 1))
                tariff_cols = [f"Tariff_{i}" for i in range(1, len(tcols) + 1)]

            else:
                first_tb = tb_range["first"] or 1
                last_tb = tb_range["last"]

                tcols = [f"TB_{i}" for i in range(first_tb, last_tb + 1)]
                tariff_cols = [f"Tariff_{i}" for i in range(first_tb, last_tb + 1)]
                x_vals = list(range(first_tb, last_tb + 1))


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
                title={
                    'text': f"Load and Tariff Profiles for Cluster {cluster} ", #| Savings %: {net_savings_pct},| Change in Retailer's Profit: ₹ {net_change_profit}",
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
        Output("cluster-load-graph-left", "figure", allow_duplicate = True),
        Input('cluster-left-tabs', 'value'),
        Input("consumer-dropdown-left", "value"),
        State("cluster-store-uploaded-file-left", "data"),
        prevent_initial_call=True
    )
    def update_consumer_plot_left(active_tab, consumer, store_data):
        if store_data is None:
            return go.Figure()

        try:

            output = pd.read_json(store_data['updated_profile_average'], orient='split')
            tariff = pd.read_json(store_data['updated_tariff'], orient = 'split')
            processing_df = pd.read_json(store_data["all_processing_df"], orient='split')

        except Exception as e:
            return go.Figure()

        if active_tab == "cluster-consumer-left":

            sub_original = output[(output['Consumer No'] == consumer) &
                                (output['Type'] == "Before Optimization")
                                ]

            sub_mod = output[(output['Consumer No'] == consumer) &
                            (output['Type'] == "After Optimization")
                            ]

            net_save_pct = output.loc[output['Consumer No'] == consumer,'net_savings%']
            net_change_profit = output.loc[output['Consumer No'] == consumer,'Change_in_Retailer_Profit']

            if not net_save_pct.empty:
                net_save_pct = round(net_save_pct.values[0], 2)
            else:
                net_save_pct = ""

            if not net_change_profit.empty:
                net_change_profit = round(net_change_profit.values[0], 2)
            else:
                net_change_profit = ""


            tb_range = TimeBlockRangeCache.get()
            if tb_range["first"] is None or tb_range["last"] is None:
                # detect existing TB columns from dataset
                tcols = sorted([col for col in sub_original.columns if col.startswith("TB_")],
                               key=lambda c: int(c.split("_")[1]))
                x_vals = list(range(1, len(tcols) + 1))
                tariff_cols = [f"Tariff_{i}" for i in range(1, len(tcols) + 1)]

            else:
                first_tb = tb_range["first"] or 1
                last_tb = tb_range["last"]

                tcols = [f"TB_{i}" for i in range(first_tb, last_tb + 1)]
                tariff_cols = [f"Tariff_{i}" for i in range(first_tb, last_tb + 1)]
                x_vals = list(range(first_tb, last_tb + 1))


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
                title={'text': f"Load and Tariff Profiles for Consumer {consumer} | Savings %: {net_save_pct} % | Change in DISCOM's Profit: ₹{net_change_profit}",
                    'font': dict(size=8)},
                xaxis_title='Hour of Day',
                yaxis_title='Load (kW)',
                autosize=True,
                #legend_title_text="Date",
                height=None,
                width=None,
                #legend_title='Legend',
                barmode='overlay',
                template='plotly_white',
                legend=dict(
                    orientation="h",    # horizontal legend
                    yanchor="top",
                    y=-0.2,             # push below the graph
                    xanchor="center",
                    x=0.5,
                    font=dict(size=9),  # smaller legend font
                    title=None          # remove "Legend" title
            )
            )

            fig.update_yaxes(title_text="Load (kW)", secondary_y=False)
            fig.update_yaxes(title_text="Tariff (₹/kWh)", secondary_y=True)
            fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

            return fig

        elif active_tab == 'cluster-total-left':

            try:
                sheet_df = output
                #cols = [f'Hour_{i}' for i in range(1, 25)]

                tb_range = TimeBlockRangeCache.get()

                if tb_range["first"] is None or tb_range["last"] is None:
                    # detect existing TB columns from dataset
                    cols = sorted([col for col in sheet_df.columns if col.startswith("TB_")],
                                   key=lambda c: int(c.split("_")[1]))
                    tcol = [i+1 for i in range(len(cols))]

                else:
                    first_tb = tb_range["first"] or 1
                    last_tb = tb_range["last"]

                    cols = [f"TB_{i}" for i in range(first_tb, last_tb + 1)]
                    tcol = [i + 1 for i in range(len(cols))]


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
                #compare_df['Hour'] = compare_df['Hour'].str.extract(r'Hour_(\d+)').astype(int)

                print(compare_df)

                fig = go.Figure()

                fig.add_trace(go.Scatter(x= tcol, y=compare_df['Before Optimization'],
                                     name='Before Optimization',line=dict(color='blue'), mode = 'lines'))

                fig.add_trace(go.Scatter(x= tcol, y=compare_df['After Optimization'],
                                     name='After Optimization', line=dict(color='green'), mode = 'lines'))

                fig.update_layout(
                    title= {'text': f"Load and Tariff Profiles for ALL consumers ", #  | Total Savings %: {total_savings_pct} %",
                    'font': dict(size=8)},
                    xaxis_title='TimeBlock of Day',
                    yaxis_title='Total Load (kW)',
                    barmode='group',
                    autosize=True,
                    height = None,
                    width = None,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=9),
                                title=None)
                )
                fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

                return fig

            except Exception as e:
                return go.Figure()


    @app.callback(
        Output("consumer-dropdown-right", "options"),
        Output("cluster-load-comparison-loading-warning-right", "children"),
        Input("cluster-store-uploaded-file-right", "data"),
        prevent_initial_call=True
    )
    def populate_consumer_dropdown_right(store_data):
        if not store_data:
            return no_update, "No file uploaded."

        sheet_df = pd.read_json(store_data["updated_profile_average"], orient='split')

        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Consumer No'].dropna().unique())]
        return opts, ""




    ######################### Populate RIGHT Category #####################################################

    @app.callback(
        Output('right-category-dropdown1', 'options'),
        Output('right-load-bin-dropdown1', 'options'),
        Output('right-consumption-bin-dropdown1', 'options'),
        Output('right-cluster-dropdown1', 'options'),

        Input("cluster-right-tabs", "value"),
        Input('right-category-dropdown1', 'value'),
        Input('right-load-bin-dropdown1', 'value'),
        Input('right-consumption-bin-dropdown1', 'value'),
        Input('right-cluster-dropdown1', 'value'),
        Input('cluster-store-uploaded-file-right', 'data')
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

        Output("cluster-load-graph-right", "figure", allow_duplicate=True),
        Input("cluster-right-tabs", "value"),
        Input('right-category-dropdown1', 'value'),
        Input('right-load-bin-dropdown1', 'value'),
        Input('right-consumption-bin-dropdown1', 'value'),
        Input('right-cluster-dropdown1', 'value'),
        State("cluster-store-uploaded-file-right", "data"),
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



            tb_range = TimeBlockRangeCache.get()
            if tb_range["first"] is None or tb_range["last"] is None:
                # detect existing TB columns from dataset
                tcols = sorted([col for col in sub_original.columns if col.startswith("TB_")],
                               key=lambda c: int(c.split("_")[1]))
                x_vals = list(range(1, len(tcols) + 1))
                tariff_cols = [f"Tariff_{i}" for i in range(1, len(tcols) + 1)]

            else:
                first_tb = tb_range["first"] or 1
                last_tb = tb_range["last"]

                tcols = [f"TB_{i}" for i in range(first_tb, last_tb + 1)]
                tariff_cols = [f"Tariff_{i}" for i in range(first_tb, last_tb + 1)]
                x_vals = list(range(first_tb, last_tb + 1))


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
                title={
                    'text': f"Load and Tariff Profiles for Cluster {cluster} ", # | Savings %: {net_savings_pct},| Change in Retailer's Profit: ₹ {net_change_profit}",
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
        Output("cluster-load-graph-right", "figure", allow_duplicate=True),
        Input("cluster-right-tabs", "value"),
        Input("consumer-dropdown-right", "value"),
        State("cluster-store-uploaded-file-right", "data"),
        prevent_initial_call=True
    )
    def update_consumer_plot_right(active_tab, consumer, store_data):

        if store_data is None:
            return go.Figure()

        try:
            output = pd.read_json(store_data['updated_profile_average'], orient='split')
            tariff = pd.read_json(store_data['updated_tariff'], orient='split')


        except Exception as e:
            return go.Figure()

        if active_tab == "cluster-consumer-right":


            sub_original = output[(output['Consumer No'] == consumer) &
                                (output['Type'] == "Before Optimization") 
                                #&
                                #(output['Month'] == month)
                                ]

            sub_mod = output[(output['Consumer No'] == consumer) &
                            (output['Type'] == "After Optimization") 
                            #&
                            #(output['Month'] == month)
                            ]
            


            #net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
            net_save_pct = output.loc[output['Consumer No'] == consumer,'net_savings%']
            net_change_profit = output.loc[output['Consumer No'] == consumer, 'Change_in_Retailer_Profit']

            if not net_save_pct.empty:
                net_save_pct = round(net_save_pct.values[0],2)
            else:
                net_save_pct = ""

            if not net_change_profit.empty:
                net_change_profit = round(net_change_profit.values[0], 2)
            else:
                net_change_profit = ""


            tb_range = TimeBlockRangeCache.get()
            if tb_range["first"] is None or tb_range["last"] is None:
                # detect existing TB columns from dataset
                tcols = sorted([col for col in sub_original.columns if col.startswith("TB_")],
                               key=lambda c: int(c.split("_")[1]))
                x_vals = list(range(1, len(tcols) + 1))
                tariff_cols = [f"Tariff_{i}" for i in range(1, len(tcols) + 1)]

            else:
                first_tb = tb_range["first"] or 1
                last_tb = tb_range["last"]

                tcols = [f"TB_{i}" for i in range(first_tb, last_tb + 1)]
                tariff_cols = [f"Tariff_{i}" for i in range(first_tb, last_tb + 1)]
                x_vals = list(range(first_tb, last_tb + 1))


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
                title={'text': f"Load and Tariff Profiles for Consumer {consumer}  | Savings %: {net_save_pct} % | Change in DISCOM's Profit: ₹{net_change_profit}",
                    'font': dict(size=8)},
                xaxis_title='Hour of Day',
                yaxis_title='Load (kW)',
                autosize=True,
                #legend_title_text="Date",
                height=None,
                width=None,
                #legend_title='Legend',
                barmode='overlay',
                template='plotly_white',
                legend=dict(
                    orientation="h",    # horizontal legend
                    yanchor="top",
                    y=-0.2,             # push below the graph
                    xanchor="center",
                    x=0.5,
                    font=dict(size=9),  # smaller legend font
                    title=None          # remove "Legend" title
            )
            )

            fig.update_yaxes(title_text="Load (kW)", secondary_y=False)
            fig.update_yaxes(title_text="Tariff (₹/kWh)", secondary_y=True)
            fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

            return fig

        elif active_tab == "cluster-total-right":

            try:
                processing_df = pd.read_json(store_data["all_processing_df"], orient='split')
                sheet_df = output

                tb_range = TimeBlockRangeCache.get()

                if tb_range["first"] is None or tb_range["last"] is None:
                    # detect existing TB columns from dataset
                    cols = sorted([col for col in sheet_df.columns if col.startswith("TB_")],
                                   key=lambda c: int(c.split("_")[1]))
                    tcol = [(i + 1) for i in range(len(cols)) ]

                else:
                    first_tb = tb_range["first"] or 1
                    last_tb = tb_range["last"]

                    cols = [f"TB_{i}" for i in range(first_tb, last_tb + 1)]
                    tcol = [(i + 1) for i in range(len(cols))]


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
                #compare_df['Hour'] = compare_df['Hour'].str.extract(r'Hour_(\d+)').astype(int)
                fig = go.Figure()

                fig.add_trace(go.Scatter(x= tcol, y=compare_df['Before Optimization'],
                                     name='Before Optimization',line=dict(color='blue'), mode = 'lines'))

                fig.add_trace(go.Scatter(x= tcol, y=compare_df['After Optimization'],
                                     name='After Optimization', line=dict(color='green'), mode = 'lines'))

                fig.update_layout(
                    title= {'text': f"Load and Tariff Profiles for ALL consumers" , # | Total Savings %: {total_savings_pct} %",
                    'font': dict(size=8)},
                    xaxis_title='TimeBlock of Day',
                    yaxis_title='Total Load (kW)',
                    barmode='group',
                    autosize=True,
                    height = None,
                    width = None,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=9),
                                title=None)
                )
                fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
                return fig

            except Exception as e:
                return go.Figure()