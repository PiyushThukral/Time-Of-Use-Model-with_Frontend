import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import os

app = dash.Dash(__name__, suppress_callback_exceptions=True)

dummy_store = {"path": "temp_data/consumer_data_demo_COM.xlsx"}

layout = html.Div([
    dcc.Store(id="store-uploaded-file", storage_type="session", data=dummy_store),
    html.Div([
        dcc.Dropdown(id="cat-dropdown", placeholder="Select Category"),
        dcc.Dropdown(id="sanction-dropdown", placeholder="Select Sanctioned Load"),
        dcc.Dropdown(id="cnumber-dropdown", placeholder="Select Consumer No"),
    ]),
    html.Div(id="logs-area")
])

app.layout = layout

def get_scenario_df():
    fp = dummy_store.get("path")
    if os.path.exists(fp):
        df = pd.read_excel(fp, parse_dates=["Date"])
        df["Date_str"] = df["Date"].dt.strftime('%Y-%m-%d')
        return df
    return None

@app.callback(
    Output("cat-dropdown", "options"),
    Output("sanction-dropdown", "options"),
    Output("cnumber-dropdown", "options"),
    Output("logs-area", "children"),
    Input("store-uploaded-file", "data"),
    prevent_initial_call=True
)
def populate_dropdowns(uploaded_file):
    df = get_scenario_df()
    if df is None:
        return [], [], [], "❌ No file found"

    return (
        [{"label": x, "value": x} for x in df["Category"].unique()],
        [{"label": x, "value": x} for x in df["Sanctioned_Load_KW"].unique()],
        [{"label": x, "value": x} for x in df["Consumer No"].unique()],
        "✅ Dropdowns loaded"
    )

if __name__ == "__main__":
    app.run_server(dev_tools_ui=False,use_reloader=False)
