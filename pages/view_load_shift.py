import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objs as go
#from pages import run_model_dashboard
from plotly.subplots import make_subplots
from pages.cache import SaveDirCache , OutputFileNameCache




# 2. layout factory stays the same (no reading at import time)
layout = html.Div([
    html.H1("Optariff: Current Model Run Result"),

    html.Label("Select Consumer"),
    dcc.Dropdown(id='consumer-dropdown', placeholder="Select a Consumer", style={'width': '50%'}),

    #html.Label("Select Month"),
    #dcc.Dropdown(id='monthly-dropdown', placeholder="Select a Month", style={'width': '50%'}),

    # wrap the graph in a Div with a vh-based height:
    html.Div(
        dcc.Graph(
            id='consumer-load-graph',
            config={'responsive': True},  # let Plotly resize to fit container
            style={'height': '90%', 'width': '100%'}
        ),
        style={
            'height': '80vh',  # use 80% of viewport height
            'width': '90%',  # optional: limit width too
            'margin': '0 auto'  # center horizontally
        }
    ),
    html.Div(id='load-loading-warning', style={'color':'red'}),
])

def register_callbacks(app):

    @app.callback(
        Output('consumer-dropdown', 'options'),
        Output('load-loading-warning', 'children'),
        Input('consumer-dropdown', 'id')   # dummy trigger
    )
    def populate_cat(_):
        
        #save_dir = tou_data.get("save_dir")
        #save_directory = run_model_dashboard.get_save_dir()
        save_directory = SaveDirCache.get()
        output_file_name_str = OutputFileNameCache.get()  # Store in cache

        #print("in load shift populating consumer no")
        if not save_directory:
            # must return here, otherwise code will keep going
            return no_update, "No Save Dir Exists"

        #output_file_path = os.path.join(save_directory, "output_file.xlsx")
        output_file_path = os.path.join(save_directory, f"{output_file_name_str}.xlsx")
        #print(f"{output_file_path}")
        if not os.path.exists(output_file_path):
            return [], f"Save dir is {save_directory} — waiting for output to be generated"

        try:
            sheet_df = pd.read_excel(
                output_file_path,
                sheet_name="updated_profile_average"
            )
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
        Output('monthly-dropdown', 'options'),
        Input('consumer-dropdown', 'id')  # just a dummy trigger to run once

    )
    def populate_month(_):
        save_directory = SaveDirCache.get()
        output_file_name_str = OutputFileNameCache.get()
        
        if not save_directory:
            # must return here, otherwise code will keep going
            return no_update

        #output_file_path = os.path.join(save_directory, "output_file.xlsx")
        output_file_path = os.path.join(save_directory,  f"{output_file_name_str}.xlsx")
        if not os.path.exists(output_file_path):
            # either return an empty list or no_update
            return []

        try:
            sheet_df = pd.read_excel(output_file_path,
                                     sheet_name="updated_profile_average")
        except Exception as e:
            return no_update


        if sheet_df is None:
            return []

        opts = [{'label': z, 'value': z} for z in sorted(sheet_df['Month'].dropna().unique())]
        return opts

    @app.callback(
        Output('consumer-load-graph', 'figure'),
        Input('consumer-dropdown','value'),
        #Input('monthly-dropdown', 'value'),
        #prevent_initial_callbacks=True

    )
    #def update_graph(consumer, months):
    def update_graph(consumer):
        #output, tariff = get_output_df()

        #save_directory = run_model_dashboard.get_save_dir()
        save_directory = SaveDirCache.get()
        output_file_name_str = OutputFileNameCache.get()
        if not save_directory:
            # must return here, otherwise code will keep going
            return no_update

        #output_file_path = os.path.join(save_directory, "output_file.xlsx")
        output_file_path = os.path.join(save_directory,  f"{output_file_name_str}.xlsx")
        
        if not os.path.exists(output_file_path):
            # either return an empty list or no_update
            return [], f"Save dir is {save_directory} and waiting for output to be generated"

        try:
            output = pd.read_excel(output_file_path,
                                     sheet_name="updated_profile_average")
            tariff = pd.read_excel(output_file_path,
                                     sheet_name="updated_tariff")
            baseline_savings = pd.read_excel(output_file_path,
                                     sheet_name="bills_baseline_df")
        except Exception as e:
            return no_update, f"Error reading file: {e}"


        if output is None or tariff is None or not consumer: # or not months:
            return go.Figure()

        sub_original = output[(output['Consumer No'] == consumer) &
                              (output['Type'] == "Before Optimization")
                              #&
                              #(output['Month'] == months)
                              ]

        sub_mod = output[(output['Consumer No'] == consumer) &
                         (output['Type'] == "After Optimization") 
                         #&
                         #(output['Month'] == months)
                         ]

        net_save = output[output['Consumer No'] == consumer]['net_savings'].unique()
        net_save_pct = output[output['Consumer No'] == consumer]['net_savings%'].unique()


        net_savings_baseline = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings'].unique()
        net_savings_baseline_pct = baseline_savings[baseline_savings['Consumer No'] == consumer]['net_savings%'].unique()

        net_change_profit = output[output['Consumer No'] == consumer]['Change_in_Retailer_Profit'].unique()

        # Define hour columns
        tcols = [f"Hour_{i}" for i in range(1, 25)]
        tariff_cols = [f"Tariff_{i}" for i in range(1, 25)]
        x_vals = list(range(1, 25))

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Load profiles (primary y-axis)
        for _, row in sub_original.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=row[tcols].tolist(),
                    mode='lines',
                    name=f"Before Optimisation {row.get('Scenario', '')}",
                    # line=dict(color='blue')
                    line=dict(color='black')
                ),
                secondary_y=False
            )

        for _, row in sub_mod.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=row[tcols].tolist(),
                    mode='lines',
                    name=f"After Optimisation {row.get('Scenario', '')}",
                    # line=dict(color='green')
                    line=dict(color='blue')
                ),
                secondary_y=False
            )

        # Tariff bars (secondary y-axis)
        tariff_original = tariff[(tariff['Consumer No'] == consumer) & (tariff['Type'] == "Before Optimization")]
        tariff_opt = tariff[(tariff['Consumer No'] == consumer) & (tariff['Type'] == "After Optimization")]

        if not tariff_original.empty:
            row = tariff_original.iloc[0]
            fig.add_trace(
                go.Bar(
                    x=x_vals,
                    y=[row[col] for col in tariff_cols],
                    name="Tariff Before Optimization",
                    # marker_color='rgba(0,0,255,0.3)',
                    marker_color = 'rgba(107,114,128,1)',
                    opacity=0.5
                ),
                secondary_y=True
            )

        if not tariff_opt.empty:
            row = tariff_opt.iloc[0]
            fig.add_trace(
                go.Bar(
                    x=x_vals,
                    y=[row[col] for col in tariff_cols],
                    name="Tariff After Optimization",
                    #marker_color='rgba(0,128,0,0.3)',
                    marker_color = 'rgba(147,197,253,1)',
                    opacity=0.5
                ),
                secondary_y=True
            )

        # Update layout

            #     fig.update_layout(
            # title={'text' : f"Consumer {consumer} | Change in Retailer's Profit: ₹{net_change_profit[0]} | <br> Savings %: {net_save_pct[0]} % to {net_savings_baseline_pct[0]} % | Savings : ₹{net_save[0]} to ₹{net_savings_baseline[0]}|",
            #        'font': dict(size=10)
            # },

        fig.update_layout(
            # title= f"Consumer {consumer} | Expected Change in DISCOM's Profit: ₹{net_change_profit[0]} | <br> Savings %: {net_save_pct[0]} % to {net_savings_baseline_pct[0]} % | Savings : ₹{net_save[0]} to ₹{net_savings_baseline[0]}|",
            title= f"Consumer {consumer} | Expected Change in DISCOM's Profit: ₹{net_change_profit[0]} | <br> Consumer Savings %: Upto {net_savings_baseline_pct[0]} % | Consumer Savings : Upto ₹{net_savings_baseline[0]}|",
            # xaxis_title='Hour of Day',
            xaxis_title='',
            yaxis_title='Consumption (kWh)',
            # yaxis_title='Load (kW)',
            legend_title='Legend',
            barmode='overlay',  # Overlay bar charts
            # template='plotly_white',
            template ='simple_white'
        )



        # Secondary y-axis
        fig.update_yaxes(
            title_text="Load (kW)", secondary_y=False
        )
        fig.update_yaxes(
            title_text="Tariff (₹/kWh)", secondary_y=True
        )


        fig.update_xaxes(
            tickmode='linear',
            tick0=1,
            dtick=1
        )

        return fig
