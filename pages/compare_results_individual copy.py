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



layout = html.Div([
    html.H1("Optariff: Individual Model Result Comparison", style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div([
        # Left Panel
        html.Div([
            html.H4("Upload Model Results (Dataset 1)"),
            dcc.Upload(
                id="upload-data-left",
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
            dcc.Store(id="store-uploaded-file-left"),
            html.Div(id="file-upload-status-left", style={"fontSize": "12px", "color": "green"}),

            html.Label("Select Consumer"),
            dcc.Dropdown(
                id='consumer-comparison-dropdown-left',
                placeholder="Select a Consumer",
                style={'width': '100%', 'marginBottom': '10px'}
            ),

            dcc.Graph(
                id='consumer-comparison-load-graph-left',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),
            html.Div(id='load-comparison-loading-warning-left', style={'color': 'red'}),

            html.Div(id='logs-area-left', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})
        ], style={'width': '48%', 'padding': '20px'}),

        # Right Panel
        html.Div([
            html.H4("Upload Model Results (Dataset 2)"),
            dcc.Upload(
                id="upload-data-right",
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
            dcc.Store(id="store-uploaded-file-right"),
            html.Div(id="file-upload-status-right", style={"fontSize": "12px", "color": "green"}),

            html.Label("Select Consumer"),
            dcc.Dropdown(
                id='consumer-comparison-dropdown-right',
                placeholder="Select a Consumer",
                style={'width': '100%', 'marginBottom': '10px'}
            ),

            dcc.Graph(
                id='consumer-comparison-load-graph-right',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),
            html.Div(id='load-comparison-loading-warning-right', style={'color': 'red'}),

            html.Div(id='logs-area-right', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})
        ], style={'width': '48%', 'padding': '20px'})

    ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '4%'})

], style={'padding': '20px'})




def register_callbacks(app):

    ####################################
    ### UPLOAD FOR LEFT PANEL
    ####################################

    @app.callback(
        Output("store-uploaded-file-left", "data"),
        Output("file-upload-status-left", "children"),
        Output("logs-area-left", "children", allow_duplicate=True),
        Input("upload-data-left", "contents"),
        State("upload-data-left", "filename"),
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
    ### UPLOAD FOR RIGHT PANEL
    ####################################

    @app.callback(
        Output("store-uploaded-file-right", "data"),
        Output("file-upload-status-right", "children"),
        Output("logs-area-right", "children", allow_duplicate=True),
        Input("upload-data-right", "contents"),
        State("upload-data-right", "filename"),
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
            file_path = os.path.join("temp_data", f"right_{filename}")

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


    ####################################
    ### GRAPH FOR LEFT PANEL
    ####################################

    # --- LEFT PANEL CALLBACKS ---

    @app.callback(
        Output('consumer-comparison-dropdown-left', 'options'),
        Output('load-comparison-loading-warning-left', 'children'),
        Input('store-uploaded-file-left', 'data')
    )
    def populate_consumer_dropdown_left(store_data):
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
        Output('consumer-comparison-load-graph-left', 'figure'),
        Input('consumer-comparison-dropdown-left', 'value'),
        Input("upload-data-left", "contents"),   ######### testing update of data and results
        State('store-uploaded-file-left', 'data')
    )
    def update_graph_left(consumer, upload_contents, store_data):
        if not consumer or not store_data:
            return go.Figure()

        file_path = store_data.get("path")
        if not os.path.exists(file_path):
            return go.Figure()

        try:
            output = pd.read_excel(file_path, sheet_name="updated_profile_average")
            tariff = pd.read_excel(file_path, sheet_name="updated_tariff")

            baseline_savings = pd.read_excel(file_path,
                                     sheet_name="bills_baseline_df")
        except Exception as e:
            return go.Figure()

        # Filter latest month for simplicity if Month is not selected
        months = output[output['Consumer No'] == consumer]['Month'].unique()
        if len(months) == 0:
            return go.Figure()
        month = months[0]  # Default to first

        sub_original = output[(output['Consumer No'] == consumer) &
                            (output['Type'] == "Before Optimization") &
                            (output['Month'] == month)]

        sub_mod = output[(output['Consumer No'] == consumer) &
                        (output['Type'] == "After Optimization") &
                        (output['Month'] == month)]

        net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
        net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique()

        net_savings_baseline = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings'].unique()
        net_savings_baseline_pct = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings%'].unique()

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
            title={'text' : f"Consumer {consumer} | Change in Retailer's Profit: ₹{net_change_profit[0]} | <br> Savings %: {net_save_pct[0]} % to {net_savings_baseline_pct[0]} % | Savings: ₹{net_save[0]} to ₹{net_savings_baseline[0]} |",
                   'font': dict(size=10)
            },
            xaxis_title='Hour of Day',
            yaxis_title='Load (kW)',
            autosize=True,
            #legend_title_text="Date",
            height=None,
            width = None,
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
    
    ########################################################################
    # --- RIGHT PANEL CALLBACKS ---

    @app.callback(
        Output('consumer-comparison-dropdown-right', 'options'),
        Output('load-comparison-loading-warning-right', 'children'),
        Input('store-uploaded-file-right', 'data')
    )
    def populate_consumer_dropdown_right(store_data):
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
        Output('consumer-comparison-load-graph-right', 'figure'),
        Input('consumer-comparison-dropdown-right', 'value'),
        Input("upload-data-right", "contents"),
        State('store-uploaded-file-right', 'data')
    )
    def update_graph_right(consumer, upload_contents, store_data):
        if not consumer or not store_data:
            return go.Figure()

        file_path = store_data.get("path")
        if not os.path.exists(file_path):
            return go.Figure()

        try:
            output = pd.read_excel(file_path, sheet_name="updated_profile_average")
            tariff = pd.read_excel(file_path, sheet_name="updated_tariff")
            baseline_savings = pd.read_excel(file_path,
                                     sheet_name="bills_baseline_df")
        except Exception as e:
            return go.Figure()

        # Filter latest month for simplicity if Month is not selected
        months = output[output['Consumer No'] == consumer]['Month'].unique()
        if len(months) == 0:
            return go.Figure()
        month = months[0]  # Default to first

        sub_original = output[(output['Consumer No'] == consumer) &
                            (output['Type'] == "Before Optimization") &
                            (output['Month'] == month)]

        sub_mod = output[(output['Consumer No'] == consumer) &
                        (output['Type'] == "After Optimization") &
                        (output['Month'] == month)]

        net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
        net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique()

        net_savings_baseline_pct = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings%'].unique()
        net_savings_baseline = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings'].unique()

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
            title={'text' : f"Consumer {consumer} | Change in Retailer's Profit: ₹{net_change_profit[0]} | <br> Savings %: {net_save_pct[0]} % to {net_savings_baseline_pct[0]} % | Savings : ₹{net_save[0]} to ₹{net_savings_baseline[0]}|",
                   'font': dict(size=10)
            },
            xaxis_title='Hour of Day',
            yaxis_title='Load (kW)',
            autosize=True,
            #legend_title_text="Date",
            height=None,
            width = None,
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


