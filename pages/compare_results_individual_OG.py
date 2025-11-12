
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objs as go
#from pages import run_model_dashboard
from plotly.subplots import make_subplots
from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
from dash import Input, Output, State
import plotly.graph_objects as go
import base64
import pandas as pd
import os
import io



layout = html.Div([
    html.H1("Optariff: Individual Model Result Comparison", style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div([

######################################## LEFT Panel ##########################################################
        html.Div([
            html.H4("Upload Results (Dataset 1)"),
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
            dcc.Store(id="store-uploaded-file-left", data = {}),
            html.Div(id="file-upload-status-left", style={"fontSize": "12px", "color": "green"}),



###################### ORIGINAL ###########################

            dcc.Tabs(id='indiv-left-tabs', value='', children=[

                dcc.Tab(label='Total', value='tab-total-left', children=[
                    # html.Div("No dropdowns required in Total tab.", style={'padding': '10px', 'fontStyle': 'italic'})
                ]),
                dcc.Tab(label='Consumer', value='tab-consumer-left', children=[
                    html.Div([
                        html.Label("Select Consumer", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='consumer-comparison-dropdown-left',
                            placeholder="Select a Consumer",
                            style={'width': '50%'}
                        ),
                    ], style={'padding': '10px'})
                ]),

            ]),

            dcc.Graph(
                id='individual-load-graph-left',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),

            html.Div(id='indiv-load-comparison-loading-warning-left', style={'color': 'red'}),

            html.Div(id='indiv-logs-area-left', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})

        ], style={'width': '48%', 'padding': '20px'}),


        ######################################## Right Panel ##########################################################
        html.Div([
            html.H4("Upload Results (Dataset 2)"),
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
            dcc.Store(id="store-uploaded-file-right", data = {}),

            html.Div(id="file-upload-status-right", style={"fontSize": "12px", "color": "green"}),



            dcc.Tabs(id='indiv-right-tabs', value='', children=[

                dcc.Tab(label='Total', value='tab-total-right', children=[
                    # html.Div("No dropdowns required in Total tab.", style={'padding': '10px', 'fontStyle': 'italic'})
                ]),

                dcc.Tab(label='Consumer', value='tab-consumer-right', children=[
                    html.Div([
                        html.Label("Select Consumer", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='consumer-comparison-dropdown-right',
                            placeholder="Select a Consumer",
                            style={'width': '50%'}
                        ),
                    ], style={'padding': '10px'})
                ]),

            ]),

            dcc.Graph(
                id='individual-load-graph-right',
                config={'responsive': True},
                style={'height': '65vh', 'width': '100%'}
            ),

            html.Div(id='indiv-load-comparison-loading-warning-right', style={'color': 'red'}),

            html.Div(id='indiv-logs-area-right', style={"fontSize": "12px", "marginTop": "10px", "color": "gray"})

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
        Output("indiv-logs-area-left", "children", allow_duplicate=True),
        Input("upload-data-left", "contents"),
        State("upload-data-left", "filename"),
        prevent_initial_call=True,
    )
    def handle_file_upload_left(contents, filename):
        if not contents or not filename.endswith(('.xlsx', '.xls')):
            return (
                no_update,
                html.Div("❌ Please upload a valid Excel file."),
                html.Div("❌ Upload failed: Invalid file format.")
            )

        try:
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
                html.Div(f"✅ Uploaded and stored all sheets from: {filename}"),
                html.Div(f"✅ {len(json_data)} sheets stored in memory (LEFT)")
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
        Output("indiv-logs-area-right", "children", allow_duplicate=True),
        Input("upload-data-right", "contents"),
        State("upload-data-right", "filename"),
        prevent_initial_call=True,
    )
    def handle_file_upload_right(contents, filename):
        if not contents or not filename.endswith(('.xlsx', '.xls')):
            return (
                no_update,
                html.Div("❌ Please upload a valid Excel file."),
                html.Div("❌ Upload failed: Invalid file format.")
            )

        try:
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
                html.Div(f"✅ Uploaded and stored all sheets from: {filename}"),
                html.Div(f"✅ {len(json_data)} sheets stored in memory (LEFT)")
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
        Output('indiv-load-comparison-loading-warning-left', 'children'),
        Input('store-uploaded-file-left', 'data')
    )
    def populate_consumer_dropdown_left(store_data):
        if not store_data:
            return no_update, "No file uploaded."

        sheet_df = pd.read_json(io.StringIO(store_data["updated_profile_average"]), orient='split')

        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Consumer No'].dropna().unique())]
        return opts, ""


    @app.callback(
        Output('individual-load-graph-left', 'figure'),
        Input('indiv-left-tabs', 'value'),
        Input('consumer-comparison-dropdown-left', 'value'),
        State('store-uploaded-file-left', 'data'),
        prevent_initial_call=False
    )
    def update_graph_left(active_tab, consumer, store_data):
        if not store_data:
            return go.Figure()

        try:
            output = pd.read_json(io.StringIO(store_data['updated_profile_average']), orient='split')
            tariff = pd.read_json(io.StringIO(store_data['updated_tariff']), orient = 'split')
            baseline_savings = pd.read_json(io.StringIO(store_data['bills_baseline_df']), orient = 'split')

        except Exception as e:
            return go.Figure()


        if active_tab == "tab-consumer-left":
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

            net_save = output[output['Consumer No'] == consumer]['net_savings'].unique().round(2)
            net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique().round(2)

            net_savings_baseline = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings'].unique().round(2)
            net_savings_baseline_pct = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings%'].unique().round(2)

            net_change_profit = output[output['Consumer No'] == consumer]['Change_in_Retailer_Profit'].unique().round(2)

            
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
                title={'text' : f"Consumer {consumer} | Expected Change in DISCOM's Profit: ₹{net_change_profit[0]} | <br> Savings %: {net_save_pct[0]} % to {net_savings_baseline_pct[0]} % | Savings: ₹{net_save[0]} to ₹{net_savings_baseline[0]} |",
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

        elif active_tab == "tab-total-left":

            try:
                bills_df = pd.read_json(store_data["bills_df"], orient='split')
                bills_before_opt = bills_df[bills_df['Type'] == "Before Optimization"]
                sheet_df = output
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

                total_bill = bills_before_opt['Energy_bill_with_existing_tariffs'].sum(axis=0) * 30
                total_savings = bills_before_opt['net_savings'].sum(axis=0)
                total_savings_pct = (total_savings / total_bill * 100).round(2)


                # Optional: Format Hour column to be numeric (Hour_1 → 1)
                compare_df['Hour'] = compare_df['Hour'].str.extract(r'Hour_(\d+)').astype(int)
                fig = go.Figure()

                fig.add_trace(go.Scatter(x=compare_df['Hour'], y=compare_df['Before Optimization'],
                                     name='Before Optimization',line=dict(color='blue'), mode = 'lines'))

                fig.add_trace(go.Scatter(x=compare_df['Hour'], y=compare_df['After Optimization'],
                                     name='After Optimization', line=dict(color='green'), mode = 'lines'))

                fig.update_layout(
                    title={
                        #'text': f"Load and Tariff Profiles for ALL consumers,  | Total Savings %: {total_savings_pct} %",
                        'text': f"Load and Tariff Profiles for ALL consumers",
                        'font': dict(size=8)},
                    xaxis_title='Hour of Day',
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

    
    ########################################################################
    # --- RIGHT PANEL CALLBACKS ---

    @app.callback(
        Output('consumer-comparison-dropdown-right', 'options'),
        Output('indiv-load-comparison-loading-warning-right', 'children'),
        Input('store-uploaded-file-right', 'data')
    )
    def populate_consumer_dropdown_right(store_data):
        if not store_data:
            return no_update, "No file uploaded."

        try:
            sheet_df = pd.read_json(io.StringIO(store_data["updated_profile_average"]), orient='split')
        except Exception as e:
            return no_update, f"Error reading file: {e}"

        if sheet_df is None or sheet_df.empty:
            return [], "Waiting for updated_profile_average sheet…"

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Consumer No'].dropna().unique())]
        return opts, ""


    @app.callback(
        Output('individual-load-graph-right', 'figure'),
        Input("indiv-right-tabs", "value"),
        Input('consumer-comparison-dropdown-right', 'value'),
        State('store-uploaded-file-right', 'data')
    )
    def update_graph_right(active_tab, consumer, store_data):
        if not store_data:
            return go.Figure()

        try:
            output = pd.read_json(io.StringIO(store_data['updated_profile_average']), orient='split')
            tariff = pd.read_json(io.StringIO(store_data['updated_tariff']), orient='split')
            baseline_savings = pd.read_json(io.StringIO(store_data['bills_baseline_df']), orient='split')

        except Exception as e:
            return go.Figure()

        if active_tab == "tab-consumer-right":
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

            net_save = output[output['Consumer No'] == consumer]['net_savings'].unique().round(2)
            net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique().round(2)

            net_savings_baseline = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings'].unique().round(2)
            net_savings_baseline_pct = baseline_savings[baseline_savings['Consumer No'] == consumer][
                'net_savings%'].unique().round(2)

            net_change_profit = output[output['Consumer No'] == consumer]['Change_in_Retailer_Profit'].unique().round(2)

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
                title={
                    'text': f"Consumer {consumer} | Expected Change in DISCOMs's Profit: ₹{net_change_profit[0]} | <br> Savings %: {net_save_pct[0]} % to {net_savings_baseline_pct[0]} % | Savings: ₹{net_save[0]} to ₹{net_savings_baseline[0]} |",
                    'font': dict(size=10)
                    },
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

        elif active_tab == "tab-total-right":

            try:
                sheet_df = output
                bills_df = pd.read_json(store_data["bills_df"], orient='split')
                bills_before_opt = bills_df[bills_df['Type'] == "Before Optimization"]
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

                total_bill = bills_before_opt['Energy_bill_with_existing_tariffs'].sum(axis=0) * 30
                total_savings = bills_before_opt['net_savings'].sum(axis=0)
                total_savings_pct = (total_savings / total_bill * 100).round(2)

                # Optional: Format Hour column to be numeric (Hour_1 → 1)
                compare_df['Hour'] = compare_df['Hour'].str.extract(r'Hour_(\d+)').astype(int)
                fig = go.Figure()

                fig.add_trace(go.Scatter(x=compare_df['Hour'], y=compare_df['Before Optimization'],
                                         name='Before Optimization', line=dict(color='blue'), mode='lines'))

                fig.add_trace(go.Scatter(x=compare_df['Hour'], y=compare_df['After Optimization'],
                                         name='After Optimization', line=dict(color='green'), mode='lines'))

                fig.update_layout(
                    title={
                        #'text': f"Load and Tariff Profiles for ALL consumers,  | Total Savings %: {total_savings_pct} %",
                        'text': f"Load and Tariff Profiles for ALL consumers",
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

