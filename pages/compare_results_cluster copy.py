import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objs as go
#from pages import run_model_dashboard
from plotly.subplots import make_subplots
from pages.cache import SaveDirCache , OutputFileNameCache


from dash import Input, Output, State, callback, no_update
from dash import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import base64
import pandas as pd
import os


import dash
from dash import dcc, html

layout = html.Div([

    html.H1("Optariff: Cluster Model Result Comparison", style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div([

        # Left Panel
        html.Div([

            html.H4("Upload Model Results (Dataset 1)"),

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

            dcc.Tabs(id='cluster-left-tabs', value='tab-total-left', children=[

                dcc.Tab(label='Total', value='tab-total-left', children=[
                    #html.Div("No dropdowns required in Total tab.", style={'padding': '10px', 'fontStyle': 'italic'})
                ]),
                dcc.Tab(label='Consumer', value='tab-consumer-left', children=[
                    html.Div([
                        html.Label("Select Consumer", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='consumer-dropdown-left',
                            placeholder="Select a Consumer",
                            style={'width': '50%'}
                        ),
                    ], style={'padding': '10px'})
                ]),

                # dcc.Tab(label='Cluster', value='tab-cluster-left', children=[
                #     html.Div([

                #         html.Div([

                #             html.Div([
                #                 html.Label("Select Category             ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='category-dropdown-left',
                #                     placeholder="Select Category",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'marginRight': '2%', 'display': 'inline-block'}),

                #             html.Div([
                #                 html.Label("Select Sanctioned Load Bin  ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='load-bin-dropdown-left',
                #                     placeholder="Select Load Bin",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'marginRight': '2%', 'display': 'inline-block'}),

                #             html.Div([
                #                 html.Label("Select Consumption Bin      ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='consumption-bin-dropdown-left',
                #                     placeholder="Select Consumption Bin",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'marginRight': '2%', 'display': 'inline-block'}),

                #             html.Div([
                #                 html.Label("Select Cluster              ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='cluster-dropdown-left',
                #                     placeholder="Select Cluster",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'display': 'inline-block'}),

                #         ], style={
                #             'display': 'flex',
                #             'flex-wrap': 'wrap',
                #             'justify-content': 'space-between',
                #             'marginBottom': '15px',
                #             'padding': '10px'
                #         }),

                #     ])
                # ]),



            ]),

            dcc.Graph(
                id='cluster-load-graph-left',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),

            html.Div(id='cluster-load-comparison-loading-warning-left', style={'color': 'red'}),

            html.Div(id='cluster-logs-area-left', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})

        ], style={'width': '48%', 'padding': '20px'}),

        # Right Panel
        html.Div([

            html.H4("Upload Model Results (Dataset 2)"),

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

            # dcc.Tabs(id='cluster-right-tabs', value='tab-consumer-right', children=[
            #     dcc.Tab(label='Consumer', value='tab-consumer-right'),
            #     dcc.Tab(label='Cluster', value='tab-cluster-right'),
            #     dcc.Tab(label='Total', value='tab-total-right'),
            # ]),

            # html.Div(id='cluster-right-panel-dropdowns', children=[]),

            dcc.Tabs(id='cluster-right-tabs', value='tab-total-right', children=[

            dcc.Tab(label='Total', value='tab-total-right', children=[
                    #html.Div("No dropdowns required in Total tab.", style={'padding': '10px', 'fontStyle': 'italic'})
                ]),

            


                dcc.Tab(label='Consumer', value='tab-consumer-right', children=[
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

                # dcc.Tab(label='Cluster', value='tab-cluster-right', children=[
                #     html.Div([

                #         html.Div([

                #             html.Div([
                #                 html.Label("Select Category             ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='category-dropdown-right',
                #                     placeholder="Select Category",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'marginRight': '2%', 'display': 'inline-block'}),

                #             html.Div([
                #                 html.Label("Select Sanctioned Load Bin  ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='load-bin-dropdown-right',
                #                     placeholder="Select Load Bin",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'marginRight': '2%', 'display': 'inline-block'}),

                #             html.Div([
                #                 html.Label("Select Consumption Bin      ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='consumption-bin-dropdown-right',
                #                     placeholder="Select Consumption Bin",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'marginRight': '2%', 'display': 'inline-block'}),

                #             html.Div([
                #                 html.Label("Select Cluster              ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                #                 dcc.Dropdown(
                #                     id='cluster-dropdown-right',
                #                     placeholder="Select Cluster",
                #                     style={'width': '100%'}
                #                 ),
                #             ], style={'width': '23%', 'display': 'inline-block'}),

                #         ], style={
                #             'display': 'flex',
                #             'flex-wrap': 'wrap',
                #             'justify-content': 'space-between',
                #             'marginBottom': '15px',
                #             'padding': '10px'
                #         }),

                #     ])
                # ]),



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

            # Save locally
            os.makedirs("temp_data", exist_ok=True)
            file_path = os.path.join("temp_data", f"left_{filename}")

            with open(file_path, "wb") as f:
                f.write(decoded)

            # Cache path if needed
            # inputfileDirCache.set(file_path)  # optional per side

            # Store file data
            store_data = {
                "filename": filename,
                "path": file_path
            }

            return (
                store_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} saved to {file_path} (LEFT)")
            )

        except Exception as e:
            return (
                no_update,
                html.Div("❌ Upload failed."),
                html.Div(f"❌ Error: {str(e)}")
            )

    ####################################
    ### UPLOAD FOR LEFT PANEL
    ####################################

    @app.callback(
        Output("cluster-store-uploaded-file-right", "data"),
        Output("cluster-file-upload-status-right", "children"),
        Output("cluster-logs-area-right", "children", allow_duplicate=True),
        Input("cluster-upload-data-right", "contents"),
        State("cluster-upload-data-right", "filename"),
        prevent_initial_call=True,
    )
    def handle_file_upload_left(contents, filename):
        if not contents:
            raise PreventUpdate

        try:
            # Decode content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Save locally
            os.makedirs("temp_data", exist_ok=True)
            file_path = os.path.join("temp_data", f"left_{filename}")

            with open(file_path, "wb") as f:
                f.write(decoded)

            # Cache path if needed
            # inputfileDirCache.set(file_path)  # optional per side

            # Store file data
            store_data = {
                "filename": filename,
                "path": file_path
            }

            return (
                store_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} saved to {file_path} (RIGHT)")
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
        #Input("cluster-left-tabs", "value"),
        Input("cluster-store-uploaded-file-left", "data"),
        State("cluster-store-uploaded-file-left", "data"),
        prevent_initial_call=True
    )
    def populate_consumer_dropdown_left(active_tab, store_data):

        print("inside populate consumer dropdown")
        #if active_tab != "tab-consumer-left" or 
        if store_data is None:
            return [], "Upload file first."

        if not store_data:
            return no_update, "No file uploaded."

        file_path = store_data.get("path")
        if not os.path.exists(file_path):
            return [], f"File {file_path} not found."

        try:
            sheet_df = pd.read_excel(file_path, sheet_name="updated_profile_average")
        except Exception as e:
            return no_update, f"Error reading file: {e}"

        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Consumer No'].dropna().unique())]
        return opts, ""

    

    @app.callback(
        Output("cluster-load-graph-left", "figure", allow_duplicate = True),
        Input("consumer-dropdown-left", "value"),
        State("cluster-store-uploaded-file-left", "data"),
        prevent_initial_call=True
    )
    def update_consumer_plot_left(consumer, store_data):
        print("test")
        if consumer is None or store_data is None:
            return go.Figure()

        try:
            print("inside  update plot")
            file_path = store_data["path"]
            output = pd.read_excel(file_path, sheet_name="updated_profile_average")
            tariff = pd.read_excel(file_path, sheet_name="updated_tariff")
            # baseline_savings = pd.read_excel(file_path,
            #                          sheet_name="bills_baseline_df")

            # Filter latest month for simplicity
            #months = output[output['Consumer No'] == consumer]['Month'].unique()
            #if len(months) == 0:
            #    return go.Figure()
            #month = months[0]

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
            
            

            net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
            net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique()

            #net_savings_baseline = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings%'].unique()

            net_change_profit = output[output['Consumer No'] == consumer]['Change_in_Retailer_Profit'].unique()

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
                title={'text': f"Load and Tariff Profiles for Consumer {consumer} | Savings %: {net_save_pct[0]} % ", # | Change in Retailer's Profit: ₹{net_change_profit[0]
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

        except Exception as e:
            return go.Figure()


    @app.callback(
        Output("consumer-dropdown-right", "options"),
        Output("cluster-load-comparison-loading-warning-right", "children"),
        #Input("cluster-right-tabs", "value"),
        Input("cluster-store-uploaded-file-right", "data"),
        State("cluster-store-uploaded-file-right", "data"),
        prevent_initial_call=True
    )
    def populate_consumer_dropdown_right(active_tab, store_data):

        print("inside populate consumer dropdown")
        #if active_tab != "tab-consumer-right" or 
        if store_data is None:
            return [], "Upload file first."

        if not store_data:
            return no_update, "No file uploaded."

        file_path = store_data.get("path")
        if not os.path.exists(file_path):
            return [], f"File {file_path} not found."

        try:
            sheet_df = pd.read_excel(file_path, sheet_name="updated_profile_average")
        except Exception as e:
            return no_update, f"Error reading file: {e}"

        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Consumer No'].dropna().unique())]
        return opts, ""

        

    @app.callback(
        Output("cluster-load-graph-right", "figure", allow_duplicate = True),
        Input("consumer-dropdown-right", "value"),
        State("cluster-store-uploaded-file-right", "data"),
        prevent_initial_call=True
    )
    def update_consumer_plot_right(consumer, store_data):
        print("test")
        if consumer is None or store_data is None:
            return go.Figure()

        try:
            print("inside  update plot")
            file_path = store_data["path"]
            output = pd.read_excel(file_path, sheet_name="updated_profile_average")
            tariff = pd.read_excel(file_path, sheet_name="updated_tariff")

            # Filter latest month for simplicity
            #months = output[output['Consumer No'] == consumer]['Month'].unique()
            #if len(months) == 0:
            #    return go.Figure()
            #month = months[0]

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
            


            net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
            net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique()
            net_change_profit = output[output['Consumer No'] == consumer]['Change_in_Retailer_Profit'].unique()

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
                title={'text': f"Load and Tariff Profiles for Consumer {consumer} | Savings %: {net_save_pct[0]} %", # | Change in Retailer's Profit: ₹{net_change_profit[0]}",
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

        except Exception as e:
            return go.Figure()



##### TOTAL TAB PLOT

    @app.callback(
        Output("cluster-load-graph-left", "figure", allow_duplicate = True),
        Input("cluster-store-uploaded-file-left", "data"),    # you commented this out, so no Input
        #State("cluster-store-uploaded-file-left", "data"),
        prevent_initial_call=True
    )
    def update_total_plot_left(store_data):
        print("test")
        if store_data is None:
            print("stcuk in none")
            return go.Figure()

        try:
            print("inside total update plot")
            file_path = store_data["path"]
            output = pd.read_excel(file_path, sheet_name="updated_profile_average")
            #tariff = pd.read_excel(file_path, sheet_name="updated_tariff")
            processing_df = pd.read_excel(file_path, sheet_name="all_processing_df")
            

            # Filter rows by type only — across all consumers
            sub_original = output[output['Type'] == "Before Optimization"]
            sub_mod = output[output['Type'] == "After Optimization"]

            # Columns for hour-wise load
            tcols = [f"Hour_{i}" for i in range(1, 25)]
            x_vals = list(range(1, 25))

            # Aggregate (sum) load across all consumers → gives one "total load profile" row
            total_original = sub_original[tcols].sum(axis=0)
            total_mod = sub_mod[tcols].sum(axis=0)

            total_bill = processing_df['energy_bill'].sum(axis=0)*30
            total_savings = processing_df['net_savings'].sum(axis=0)

            total_savings_pct = (total_savings/total_bill*100).round(1)

            print(total_savings_pct)

            # Now plot
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Plot total "Before Optimization"
            fig.add_trace(
                go.Scatter(x=x_vals, y=total_original.tolist(), mode='lines',
                        name="Total Before Optimization", line=dict(color='blue', width=3)),
                secondary_y=False
            )

            # Plot total "After Optimization"
            fig.add_trace(
                go.Scatter(x=x_vals, y=total_mod.tolist(), mode='lines',
                        name="Total After Optimization", line=dict(color='green', width=3)),
                secondary_y=False
            )

            fig.update_layout(
                title={'text': f"Load and Tariff Profiles for ALL consumers,  | Total Savings %: {total_savings_pct} %", 
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

        except Exception as e:
            print(f"Error in update_total_plot_left: {e}")
            return go.Figure()



    ##### TOTAL TAB PLOT

    @app.callback(
        Output("cluster-load-graph-right", "figure", allow_duplicate = True),
        Input("cluster-store-uploaded-file-right", "data"),    # you commented this out, so no Input
        #State("cluster-store-uploaded-file-right", "data"),
        prevent_initial_call=True
    )
    def update_total_plot_right(store_data):
        print("test")
        if store_data is None:
            print("stcuk in none")
            return go.Figure()

        try:
            print("inside total update plot")
            file_path = store_data["path"]
            output = pd.read_excel(file_path, sheet_name="updated_profile_average")
            #tariff = pd.read_excel(file_path, sheet_name="updated_tariff")
            processing_df = pd.read_excel(file_path, sheet_name="all_processing_df")

            # Filter rows by type only — across all consumers
            sub_original = output[output['Type'] == "Before Optimization"]
            sub_mod = output[output['Type'] == "After Optimization"]

            # Columns for hour-wise load
            tcols = [f"Hour_{i}" for i in range(1, 25)]
            x_vals = list(range(1, 25))

            # Aggregate (sum) load across all consumers → gives one "total load profile" row
            total_original = sub_original[tcols].sum(axis=0)
            total_mod = sub_mod[tcols].sum(axis=0)

            total_bill = processing_df['energy_bill'].sum(axis=0)*30
            total_savings = processing_df['net_savings'].sum(axis=0)

            total_savings_pct = (total_savings/total_bill*100).round(1)

            print(total_savings_pct)

            # Now plot
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Plot total "Before Optimization"
            fig.add_trace(
                go.Scatter(x=x_vals, y=total_original.tolist(), mode='lines',
                        name="Total Before Optimization", line=dict(color='blue', width=3)),
                secondary_y=False
            )

            # Plot total "After Optimization"
            fig.add_trace(
                go.Scatter(x=x_vals, y=total_mod.tolist(), mode='lines',
                        name="Total After Optimization", line=dict(color='green', width=3)),
                secondary_y=False
            )

            fig.update_layout(
                title={'text': f"Load and Tariff Profiles for ALL consumers | Total Savings %: {total_savings_pct} %", #", # | Change in Retailer's Profit: ₹{net_change_profit[0]
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
            #fig.update_yaxes(title_text="Tariff (₹/kWh)", secondary_y=True)
            fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)

            return fig

        except Exception as e:
            print(f"Error in update_total_plot_right: {e}")
            return go.Figure()

