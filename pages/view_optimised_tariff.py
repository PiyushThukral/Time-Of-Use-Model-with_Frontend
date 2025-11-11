import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
#from pages import run_model_dashboard

# 1. lazy‐loader for your DataFrame
output_file = None
def get_output_df():
    global output_file
    if output_file is None:
        save_dir = run_model_dashboard.get_save_dir()
        fp = os.path.join(save_dir, 'output_file.xlsx' )
        if os.path.exists(fp):
            df = pd.read_excel(
                fp,
                sheet_name="updated_tariff",

            )
            output_file = df
    return output_file

# 2. layout factory stays the same (no reading at import time)
layout = html.Div([
    html.H1("Optimised Tariffs"),

    html.Label("Select Consumer"),
    dcc.Dropdown(id='consumer-tariff-dropdown', placeholder="Select a Consumer", style={'width': '50%'}),

    # wrap the graph in a Div with a vh-based height:
    html.Div(
        dcc.Graph(
            id='tariff-load-graph',
            config={'responsive': True},  # let Plotly resize to fit container
            style={'height': '90%', 'width': '100%'}
        ),
        style={
            'height': '80vh',  # use 80% of viewport height
            'width': '90%',  # optional: limit width too
            'margin': '0 auto'  # center horizontally
        }
    ),
    html.Div(id='tariff-loading-warning', style={'color':'red'})
])

def register_callbacks(app):
    @app.callback(
        Output('consumer-tariff-dropdown', 'options'),
        Output('tariff-loading-warning', 'children'),
        Input('consumer-tariff-dropdown', 'id')  # just a dummy trigger to run once
    )
    def populate_cat(_):
        output = get_output_df()
        if output is None:
            return [], "Waiting for Ouput.xlsx to appear in save_dir…"
        opts = [{'label': z, 'value': z} for z in sorted(output['Consumer No'].dropna().unique())]
        return opts, ""

    @app.callback(
        Output('tariff-load-graph', 'figure'),
        Input('consumer-tariff-dropdown','value'),

    )


    def update_graph(consumer):
        output = get_output_df()

        if output is None or not consumer:
            return go.Figure()

        sub_original = output[(output['Consumer No'] == consumer) & (output['Type'] == "Before Optimization")]
        sub_opt = output[(output['Consumer No'] == consumer) & (output['Type'] == "After Optimization")]

        tcols = [f"Tariff_{i}" for i in range(1, 25)]
        xcols = [f'Hour_{i}' for i in range(1,25)]
        fig = go.Figure()

        if not sub_original.empty:
            row = sub_original.iloc[0]  # Take the first row if multiple exist
            fig.add_trace(go.Bar(
                x=xcols,
                y=[row[col] for col in tcols],
                name="Before Optimization"
            ))

        if not sub_opt.empty:
            row = sub_opt.iloc[0]
            fig.add_trace(go.Bar(
                x=xcols,
                y=[row[col] for col in tcols],
                name="After Optimization"
            ))

        fig.update_layout(
            title=f"Tariff Comparison for Consumer {consumer}",
            xaxis_title='Tariff Period',
            yaxis_title='₹/kWh',
            barmode='group',  # Shows bars side by side
            template='plotly_white'
        )

        return fig
