from dash import html, dcc, dash_table, Input, Output, State, no_update
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.parse import quote
import threading
import os
import sys
from io import StringIO
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import datetime
import pandas as pd
import dash
import plotly.graph_objects as go

file_path = ""


def preprocess_mustrun_trajectory():
    sheet_max = "MustRunTrajectoryMax"
    sheet_min = "MustRunTrajectoryMin"
    mustrun_max_df = pd.read_excel(file_path, sheet_name=sheet_max, skiprows=4)
    mustrun_min_df = pd.read_excel(file_path, sheet_name=sheet_min, skiprows=4)
    for df in [mustrun_max_df, mustrun_min_df]:
        df.rename(columns={df.columns[0]: "Zone"}, inplace=True)
        df.rename(columns={df.columns[1]: "Technology"}, inplace=True)
        df.columns = df.columns.astype(str)
        df.dropna(axis=1, how="all", inplace=True)

    years_max = [col for col in mustrun_max_df.columns if col.isdigit()]
    years_min = [col for col in mustrun_min_df.columns if col.isdigit()]

    for df, years in [(mustrun_max_df, years_max), (mustrun_min_df, years_min)]:
        for col in years:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(0).astype("Int64")

    zones = sorted(mustrun_max_df["Zone"].dropna().unique().tolist())
    technologies = sorted(mustrun_max_df["Technology"].dropna().unique().tolist())

    return mustrun_max_df, mustrun_min_df, years_max, years_min, zones, technologies


def preprocess_mustrun_trajectory_state(sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=4)
    df.rename(columns={df.columns[0]: "Technology"}, inplace=True)
    df.columns = df.columns.astype(str)
    df.dropna(axis=1, how="all", inplace=True)
    years = [col for col in df.columns[1:] if col.isdigit()]

    for col in years:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(0).astype("Int64")

    return df, years


# Extract mappings for various sheets
def get_mappings(sheet_name, cols, col_names):
    df = pd.read_excel(
        file_path, sheet_name=sheet_name, skiprows=4, usecols=cols
    ).dropna()
    df.columns = col_names
    df[col_names[1]] = pd.to_numeric(df[col_names[1]], errors="coerce").astype("Int64")
    return df


# Function to load and process Thermal data
def get_thermal_data(thermal_index_df):
    df = pd.read_excel(file_path, sheet_name="Thermal", skiprows=4)
    df = df[["Plant", "Capacity", "Planned", "StrYr", "FuelIndex"]]
    df.rename(columns={"FuelIndex": "Fuel Index"}, inplace=True)
    df = df.merge(thermal_index_df, on="Fuel Index", how="left")
    return df.groupby("Fuel Type", as_index=False).agg(
        {"Capacity": "sum", "Planned": "sum"}
    )


# Function to load and process Hydro data
def get_hydro_data(hydro_index_df):
    df = pd.read_excel(file_path, sheet_name="Hydro", skiprows=4)
    df = df[["Plant", "Capacity", "Planned", "StrYr", "Type"]]
    df.rename(columns={"Type": "Type Index"}, inplace=True)
    df["Type Index"] = pd.to_numeric(df["Type Index"], errors="coerce").astype("Int64")
    df = df.merge(hydro_index_df, on="Type Index", how="left")
    return df.groupby("Fuel Type", as_index=False).agg(
        {"Capacity": "sum", "Planned": "sum"}
    )


# Function to load and process MustRun data
def get_must_run_data(must_run_index_df):
    df = pd.read_excel(file_path, sheet_name="MustRun", skiprows=4)
    df = df[["TypeIndex", "Capacity"]]
    df.rename(columns={"TypeIndex": "Type Index"}, inplace=True)
    df["Type Index"] = pd.to_numeric(df["Type Index"], errors="coerce").astype("Int64")
    df = df.merge(must_run_index_df, on="Type Index", how="left")
    return df.groupby("Technology", as_index=False).agg({"Capacity": "sum"})


# Function to load and process RPO data
def get_rpo_data():
    df = pd.read_excel(file_path, sheet_name="RPO", skiprows=4).dropna(
        how="all", axis=1
    )
    df.rename(columns={df.columns[0]: "Year"}, inplace=True)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    return df.set_index("Year") * 100  # Convert to percentage


# Function to load and process Storage data
def get_storage_data(storage_index_df):

    df = pd.read_excel(
        file_path,
        sheet_name="Storage",
        skiprows=4,
        usecols=["TypeIndex", "Capacity", "Storage", "Energy_Capacity", "Planned"]
    )
    df.columns = [
        "Type Index",
        "Capacity (MW)",
        "Storage Duration (hrs)",
        "Energy Capacity (MWh)",
        "Planned Capacity (MW)",
    ]
    df["Type Index"] = pd.to_numeric(df["Type Index"], errors="coerce").astype("Int64")
    df = df.merge(storage_index_df, on="Type Index", how="left")
    df["Planned Energy Capacity (MWh)"] = (
        df["Planned Capacity (MW)"] * df["Storage Duration (hrs)"]
    )
    return df.groupby("Storage Technology", as_index=False).agg(
        {
            "Capacity (MW)": "sum",
            "Planned Capacity (MW)": "sum",
            "Energy Capacity (MWh)": "sum",
            "Planned Energy Capacity (MWh)": "sum",
        }
    )


def get_storage_targets_data():
    df = pd.read_excel(file_path, sheet_name="MinimumStorageTargets", skiprows=4)
    df.rename(columns={df.columns[0]: "Technology"}, inplace=True)
    df.columns = df.columns.astype(str)
    df.dropna(axis=1, how="all", inplace=True)
    years = [col for col in df.columns[1:] if col.isdigit()]

    for col in years:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(0).astype("Int64")

    return df

def plot_demand_frequency(df):
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=df["Demand (MW)"], nbinsx=50, marker_color="blue", opacity=0.75)
    )

    fig.update_layout(
        title="Demand Distribution",
        xaxis_title="Demand (MW)",
        yaxis_title="Frequency",
        template="plotly_white",
    )
    return fig


def process_demand_frequency(file_path):
    df = pd.read_excel(file_path, sheet_name="Demand_freq_dist", skiprows=4)
    if df.empty:
        return go.Figure(), [], []
    fig = plot_demand_frequency(df)
    data = df.to_dict("records")
    columns = [{"name": col, "id": col} for col in df.columns]
    return fig, data, columns
def process_demand_frequency_variation(file_path):
    df = pd.read_excel(file_path, sheet_name="Demand_freq_variation", skiprows=4)
    if df.empty:
        return go.Figure(), [], []
        # Step 1: Normalize both demand columns
    df["Normalized Demand (MW)"] = df["Demand (MW)"] / df["Demand (MW)"].max()
    df["Normalized Demand Previous Year (MW)"] = df["Demand Previous Year (MW)"] / df["Demand Previous Year (MW)"].max()

    # Step 2: Calculate Hourly Variations (%) based on normalized values
    df["Hourly Variations (%)"] = (
        (df["Normalized Demand (MW)"] - df["Normalized Demand Previous Year (MW)"]) /
        df["Normalized Demand Previous Year (MW)"]
    ) * 100

    df["Hourly Variations (%)"] = df["Hourly Variations (%)"].round(2)
    fig = plot_demand_variation(df)
    data = df.to_dict("records")
    columns = [{"name": col, "id": col} for col in df.columns]
    return fig, data, columns

def plot_demand_frequency(df):
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=df["Demand (MW)"], nbinsx=50,marker=dict(color="lightblue", opacity=0.75, line=dict(color='black', width=1)))
    )
    fig.update_layout(
        title="Demand Distribution",
        xaxis_title="Demand (MW)",
        yaxis_title="Frequency",
        template="plotly_white",
        font=dict(
        family="Arial",  # or any font you prefer
        size=20,        # base font size
        color="black"
        ),
        # Title font settings
        title_font=dict(
            size=25,
            color='black'
        ),
        # Axis titles
        xaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=20),
        ),
        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=20)
        ),
        # Legend font settings
        legend=dict(
            title_font=dict(size=20),
            font=dict(size=20)
        )
    )
    return fig

def plot_demand_variation(df):
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=df["Hourly Variations (%)"], nbinsx=50,marker=dict(color="lightblue", opacity=0.75, line=dict(color='black', width=1)))
    )
    fig.update_layout(
        title="Hourly Variations (%) Distribution",
        xaxis_title="Hourly Variations (%)",
        yaxis_title="Frequency",
        template="plotly_white",
        font=dict(
        family="Arial",  # or any font you prefer
        size=20,        # base font size
        color="black"
        ),
        # Title font settings
        title_font=dict(
            size=25,
            color='black'
        ),
        # Axis titles
        xaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=20),
        ),
        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(size=20)
        ),
        # Legend font settings
        legend=dict(
            title_font=dict(size=20),
            font=dict(size=20)
        )
    )
    return fig    


save_confirmation_modal = html.Div(
    [
        html.Div(
            [
                html.Div(
                    children=[
                        html.Div(
                            "Confirm Save",
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "padding": "15px",
                                "borderBottom": "1px solid #e0e0e0",
                                "fontWeight": "bold",
                            },
                        ),
                        html.Div(
                            [
                                html.P("Are you sure you want to save this file?"),
                                html.Div(
                                    [
                                        html.Button(
                                            "Cancel",
                                            id="close-save-modal",
                                            style={
                                                "marginRight": "10px",
                                                "padding": "8px 16px",
                                                "backgroundColor": "#f0f0f0",
                                                "border": "none",
                                                "borderRadius": "4px",
                                            },
                                        ),
                                        html.Button(
                                            "Confirm",
                                            id="confirm-save-btn",
                                            style={
                                                "padding": "8px 16px",
                                                "backgroundColor": "#134A94",
                                                "color": "white",
                                                "border": "none",
                                                "borderRadius": "4px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justifyContent": "flex-end",
                                        "marginTop": "20px",
                                    },
                                ),
                            ],
                            style={"padding": "20px"},
                        ),
                    ],
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "8px",
                        "width": "400px",
                        "maxWidth": "90%",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
                    },
                )
            ],
            id="save-confirmation-modal",
            style={
                "position": "fixed",
                "top": "50%",
                "left": "50%",
                "transform": "translate(-50%, -50%)",
                "zIndex": "1001",
                "display": "none",
            },
        ),
        html.Div(
            id="modal-overlay",
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0,0,0,0.5)",
                "zIndex": "1000",
                "display": "none",
            },
        ),
    ]
)

edit_modal = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Edit table details",
                            style={
                                "margin": "10px",
                                "marginBottom": 0,
                                "padding": "10px",
                            },
                        ),
                        html.Div(
                            dash_table.DataTable(
                                id="modal-editable-table",
                                columns=[],
                                data=[],
                                editable=True,
                                style_table={
                                    "overflowX": "auto",
                                    "overflowY": "auto",
                                    "height": "60vh",
                                    "width": "100%",
                                },
                                style_cell={
                                    "minWidth": "100px",
                                    "width": "100px",
                                    "maxWidth": "100px",
                                    "height": "20px",
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                    "whiteSpace": "normal",
                                    "textAlign": "left",
                                    "padding": "4px",
                                    "border": "1px solid #ddd",
                                },
                                style_header={
                                    "backgroundColor": "#C4DAF7",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "padding": "4px",
                                    "border": "1px solid #85B3EF",
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"state": "active"},
                                        "backgroundColor": "rgba(0, 116, 217, 0.3)",
                                        "border": "1px solid rgb(0, 116, 217)",
                                    },
                                ],
                            ),
                            style={"padding": "20px"},
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Cancel",
                                    id="cancel-edit-btn",
                                    style={
                                        "width": "150px",
                                        "height": "35px",
                                        "padding": "5px",
                                        "borderRadius": "10px",
                                        "marginRight": "10px",
                                        "backgroundColor": "#FFFFFF",
                                        "border": "1px solid black",
                                    },
                                ),
                                html.Button(
                                    "Save Changes",
                                    id="save-table-btn",
                                    style={
                                        "width": "150px",
                                        "height": "35px",
                                        "padding": "5px",
                                        "borderRadius": "10px",
                                        "backgroundColor": "#134A94",
                                        "color": "white",
                                        "border": "none",
                                    },
                                ),
                            ],
                            style={
                                "padding": "20px",
                                "display": "flex",
                                "justifyContent": "flex-end",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "10px",
                        "width": "80%",
                        "margin": "auto",
                        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",
                    },
                ),
            ],
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0, 0, 0, 0.5)",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "zIndex": "1000",
            },
        ),
    ],
    id="edit-modal",
    style={"display": "none"},
)



stellar_notification = html.Div(
    [
        html.Div(
            [
                # Left side with text
                html.Span(
                    "Optariff is Currently Running",
                    style={
                        "verticalAlign": "middle",
                        "fontWeight": "600",
                        "color": "#333",
                    },
                ),
                # Right side with your existing spinner
                html.Div(
                    id="loading-animation-run-model-modal",
                    className="model-running-spinner",
                    # The style for this will be controlled by the callback
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "gap": "1vw",
                "width": "100%",
            },
        )
    ],
    id="stellar-running-notification",
    style={"display": "none"},
)

compressed_sidebar_children = [
    html.Div(
        style={
            "marginTop": 0,
            "display": "flex",
            "flex-direction": "column",
            "alignItems": "center",
        },
        children=[
            html.Img(
                src="assets/Stellar Logo.png",
                style={
                    "height": "8vh",
                    "widht": "4vw",
                    "margin-top": "1vh",
                },
            ),
            html.Div(
                style = {"display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "4vh",},
                children = [
                dcc.Link(
                    html.Img(
                        src="assets/Run model icon.png",
                        style={
                            "height": "3vh",
                            "widht": "2vw",
                            "border": "none",
                            "border-radius": "10px",
                        },
                    ),
                    href="/run-model",
                ),
                html.Div(
                        id="loading-animation-run-model",
                        className="model-running-spinner",
                    ),
                ]
            ),
            html.Div(
                style={
                    "height": "2.8vh",
                    "widht": "2vw",
                    "background": "#FFFFFF",
                    "border": "none",
                    "padding": "10px",
                    "border-radius": "10px",
                    "margin-top": "2vh",
                },
                children=[
                    html.Img(
                        src="assets/Input Dash blue.png",
                        style={
                            "height": "3vh",
                            "widht": "2vw",
                        },
                    ),
                ],
            ),
            dcc.Link(
                html.Img(
                    src="assets/output dash icon.png",
                    style={
                        "height": "2vh",
                        "widht": "1vw",
                        "border": "none",
                        "margin-top": "2vh",
                    },
                ),
                href="/output-dashboard",
            ),
            dcc.Link(
                html.Img(
                    src="assets/help icon.png",
                    style={
                        "height": "3vh",
                        "widht": "2vw",
                        "border": "none",
                        "position": "absolute",
                        "bottom": "25vh",
                        "left": "50%",
                        "transform": "translateX(-50%)",
                    },
                ),
                href="/help",
            ),
            dcc.Link(
                html.Img(
                    src="assets/faq_icon.png",
                    style={
                        "height": "3vh",
                        "widht": "2vw",
                        "border": "none",
                        "position": "absolute",
                        "bottom": "20vh",
                        "left": "50%",
                        "transform": "translateX(-50%)",
                    },
                ),
                href="/faq",
            ),
            dcc.Link(
                html.Img(
                    src="assets/logout icon.png",
                    style={
                        "height": "2.5vh",
                        "widht": "1.6vw",
                        "border": "none",
                        "position": "absolute",
                        "bottom": "15vh",
                        "left": "50%",
                        "transform": "translateX(-50%)",
                    },
                ),
                href="/",
            ),
        ],
    ),
]

sidebar_children = [
    html.Div(
        style={
            "margin-top": "1vh",
            "display": "flex",
            "flex-direction": "column",
            "alignItems": "center",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "0.1vw",
                    "padding": "5px",
                    "width": "10vw",
                },
                children=[
                    html.Img(
                        src="assets/Stellar Logo.png",
                        style={
                            "height": "6vh",
                            "width": "3vw",
                        },
                    ),
                    html.H2("Optariff"),
                ],
            ),
            html.Div(
                children=[
            dcc.Link(
                html.Div(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "width": "10vw",
                        "marginTop": "2.5vh",
                        "border": "none",
                        "border-radius": "5px",
                        "padding": "5px",
                        "color": "black",
                        "background": "#E6F0F9",
                        "gap": "0.5vw",
                    },
                    children=[
                        html.Img(
                            src="assets/Run model icon.png",
                            style={
                                "height": "3vh",
                                "width": "1.5vw",
                            },
                        ),
                        html.Button(
                            "Run Model",
                            style={
                                "border": "none",
                                "background": "#E6F0F9",
                                "cursor": "pointer",
                                "padding": "0",
                            },
                        ),
                        html.Div(
                            id="loading-animation-run-model",
                            className="model-running-spinner",
                        ),
                    ],
                ),
                href="/run-model",
                style={"text-decoration": "none"},
            ),
            html.Div(
                style={
                    "margin-top": "2vh",
                    "display": "flex",
                    "align-items": "center",
                    "width": "10vw",
                    "border": "none",
                    "border-radius": "5px",
                    "height": "4vh",
                    "padding": "5px",
                    "color": "#134A94",
                    "background": "#FFFFFF",
                    "gap": "0.5vw",
                },
                children=[
                    html.Img(
                        src="assets/Input Dash blue.png",
                        style={
                            "height": "3vh",
                            "width": "1.5vw",
                        },
                    ),
                    html.Button(
                        "Input Dashboard",
                        style={
                            "border": "none",
                            "fontWeight": 700,
                            "color": "#134A94",
                            "background": "#FFFFFF",
                            "cursor": "pointer",
                            "padding": "0",
                        },
                    ),
                ],
            ),
            dcc.Link(
                html.Div(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "width": "10vw",
                        "marginTop": "2vh",
                        "border": "none",
                        "border-radius": "5px",
                        "padding": "5px",
                        "color": "black",
                        "background": "#E6F0F9",
                        "gap": "0.5vw",
                    },
                    children=[
                        html.Img(
                            src="assets/output dash icon.png",
                            style={
                                "height": "2.1vh",
                                "width": "1vw",
                                "marginLeft": "0.4vw",
                            },
                        ),
                        html.Button(
                            "Output Dashboard",
                            style={
                                "border": "none",
                                "background": "#E6F0F9",
                                "cursor": "pointer",
                                "padding": "0",
                            },
                        ),
                    ],
                ),
                href="/output-dashboard",
                style={"text-decoration": "none"},
            ),
            ],
                style={"position": "absolute", "top": "11vh"},
            ),
            dcc.Link(
                html.Div(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "width": "10vw",
                        "position": "absolute",
                        "bottom": "25vh",
                        "left": "55%",
                        "transform": "translateX(-50%)",
                        "border": "none",
                        "border-radius": "5px",
                        "padding": "5px",
                        "color": "black",
                        "background": "#E6F0F9",
                        "gap": "0.5vw",
                    },
                    children=[
                        html.Img(
                            src="assets/help icon.png",
                            style={
                                "height": "3vh",
                                "width": "1.5vw",
                            },
                        ),
                        html.Button(
                            "Help",
                            style={
                                "border": "none",
                                "background": "#E6F0F9",
                                "cursor": "pointer",
                                "padding": "0",
                            },
                        ),
                    ],
                ),
                href="/help",
                style={"text-decoration": "none"},
            ),
            dcc.Link(
                html.Div(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "width": "10vw",
                        "position": "absolute",
                        "bottom": "20vh",
                        "border": "none",
                        "border-radius": "5px",
                        "left": "55%",
                        "transform": "translateX(-50%)",
                        "padding": "5px",
                        "color": "black",
                        "background": "#E6F0F9",
                        "gap": "0.5vw",
                    },
                    children=[
                        html.Img(
                            src="assets/faq_icon.png",
                            style={
                                "height": "2.5vh",
                                "width": "1.3vw",
                            },
                        ),
                        html.Button(
                            "FAQ",
                            style={
                                "border": "none",
                                "background": "#E6F0F9",
                                "cursor": "pointer",
                                "padding": "0",
                            },
                        ),
                    ],
                ),
                href="/faq",
                style={"text-decoration": "none"},
            ),
            dcc.Link(
                html.Div(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "width": "10vw",
                        "position": "absolute",
                        "bottom": "15vh",
                        "border": "none",
                        "border-radius": "5px",
                        "left": "55%",
                        "transform": "translateX(-50%)",
                        "padding": "5px",
                        "color": "black",
                        "background": "#E6F0F9",
                        "gap": "0.5vw",
                    },
                    children=[
                        html.Img(
                            src="assets/logout icon.png",
                            style={
                                "height": "2.3vh",
                                "width": "1.3vw",
                            },
                        ),
                        html.Button(
                            "Logout",
                            style={
                                "border": "none",
                                "background": "#E6F0F9",
                                "cursor": "pointer",
                                "padding": "0",
                            },
                        ),
                    ],
                ),
                href="/",
                style={"text-decoration": "none"},
            ),
        ],
    ),
]

filter_area_children = [
    html.Div(
        [
            dcc.Dropdown(
                id="zone-selector",
                options=[],
                multi=False,
                placeholder="Zone",
            ),
        ],
        id="zone-selector-container",
        style={"display": "none"},
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="plant-selector",
                options=[],
                multi=True,
                placeholder="Plant",
            ),
        ],
        id="plant-selector-container",
        style={"display": "none"},
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="tech-selector", options=[], multi=False, placeholder="Technology"
            ),
        ],
        id="tech-selector-container",
        style={"display": "none"},
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="year-selector",
                options=[],
                multi=False,
                placeholder="Year",
            ),
        ],
        id="year-selector-container",
        style={"display": "none"},
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="quarter-selector",
                options=[],
                multi=False,
                placeholder="Quarter",
            ),
        ],
        id="quarter-selector-container",
        style={"display": "none"},
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="day-selector",
                options=[],
                multi=False,
                placeholder="Day",
            ),
        ],
        id="day-selector-container",
        style={"display": "none"},
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="storage-selector", options=[], multi=False, placeholder="Storage"
            ),
        ],
        id="storage-selector-container",
        style={"display": "none"},
    ),
]

layout = html.Div(
    style={
        "backgroundColor": "#FAF9F9",
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "width": "100vw",
        "margin": 0,
        "padding": 0,
        "overflow": "hidden",
        "position": "fixed",
        "top": 0,
        "left": 0,
    },
    children=[
        edit_modal,
        save_confirmation_modal,
        html.Div(
            id="input-dashboard-topbar",
            style={
                "backgroundColor": "#FFFFFF",
                "height": "10vh",
                "width": "87vw",
                "position": "absolute",
                "top": 0,
                "right": 0,
                "border": "1px solid #D1D5DB",
                "display": "flex",
                "align-items": "center",
            },
            children=[
                html.Img(
                    src="assets/CEA logo.png",
                    style={
                        "height": "7vh",
                        "width": "20vw",
                        "marginLeft": "2vw",
                    },
                ),
            ],
        ),
        html.Div(
            id="input-dashbaord-sidebar",
            style={
                "backgroundColor": "#E6F0F9",
                "height": "100vh",
                "width": "13vw",
                "position": "absolute",
                "bottom": 0,
                "left": 0,
                "border": "none",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "borderRight": "1px solid #D1D5DB",
            },
            children=sidebar_children,
        ),
        html.Div(
            id="input-dashbaord-sheet-selector",
            style={},
            children=[],
        ),
        html.Div(
            id="input-dashboard-container",
            style={
                "position": "absolute",
                "top": "10vh",
                "left": "13vw",
                "width": "calc(100vw - 13vw)",
                "height": "calc(87vh - 0vh)",
                "display": "flex",
                "flexDirection": "column",
            },
            children=[
                # selector container for project name and input file
                html.Div(
                    id = "input-dashbaord-selector-container",
                    style={
                        "backgroundColor": "#FFFFFF",
                        "height": "20vh",
                        "maxHeight": "150px",
                        "flex-shrink": 0,
                        "width": "95%",
                        "borderRadius": "10px",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                        "border": "1px solid #E4E4E4",
                        "paddingTop": "5px",
                        "display": "flex",
                        "flex-direction": "column",
                        "gap": "10px",
                        "margin-top": "3vh",
                        "margin-bottom": 0,
                        "boxSizing": "border-box",
                    },
                    children=[
                        html.Div(
                            style={
                                "width": "97%",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                                "display": "flex",
                                "alignItems": "center",
                                "margin-top": "10px",
                                "gap": "1.5vw",
                            },
                            children=[
                                html.H3("Project Name", style={"fontSize": "14px", "width": "10%",}),
                                dcc.Input(
                                    id="project-name",
                                    type="text",
                                    placeholder="Enter Project Name",
                                    style={
                                        "border": "0.5px solid #6B7480",
                                        "fontSize": "12px",
                                        "background-color": "transparent",
                                        "color": "#B2B2B2",
                                        "height": "25px",
                                        "width": "90%",
                                        "border-radius": "10px",
                                        "padding": "5px",
                                        "paddingLeft": "1%",
                                        "display": "flex",
                                        "alignItems": "center",
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                "width": "97%",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                                "display": "flex",
                                "alignItems": "center",
                                "gap": "1.5vw",
                            },
                            children=[
                                html.H3("Input File", style={"fontSize": "14px", "width": "10%",}),
                                html.Div(
                                    id="selected-input-file-path",
                                    style={
                                        "border": "0.5px solid #6B7480",
                                        "fontSize": "12px",
                                        "background-color": "transparent",
                                        "color": "#B2B2B2",
                                        "height": "25px",
                                        "width": "75%",
                                        "border-radius": "10px",
                                        "padding": "5px",
                                        "paddingLeft": "1%",
                                        "fontSize": "12px",
                                        "display": "flex",
                                        "alignItems": "center",
                                    },
                                ),
                                html.Div(
                                    children=[
                                        html.Button(
                                            "Upload",
                                            id="upload-input-file-btn",
                                            n_clicks=0,
                                            style={
                                                "border": "none",
                                                "borderRadius": "10px", 
                                                "color": "#374251",
                                                "background": "#FFFFFF",
                                                "height": "100%",
                                                "width": "100%",
                                            },
                                        )
                                    ],
                                    style={
                                         "display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "width": "15%",
                                        "height": "25px",
                                        "padding": "5px",
                                        "border": "1px solid #374251",
                                        "borderRadius": "10px", 
                                        "background": "#FFFFFF",
                                    }
                                )
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="input-content-container",
                    style={
                        "display": "none",
                    },
                    children=[
                        html.Div(
                            id="input-visual-container",
                            style={
                                "backgroundColor": "#FFFFFF",
                                "borderRadius": "10px",
                                "border": "1px solid #E4E4E4",
                                "padding": "10px",
                                "height": "90%",
                                "display": "flex", 
                                "flexDirection": "column",
                                "boxSizing": "border-box",
                            },
                            children=[
                                # filter
                                html.Div(
                                    id="input-filter-area",
                                    children=filter_area_children,
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "gap": "10px",
                                        "margin": 0,
                                        "marginLeft": "5px",
                                    },
                                ),
                                html.Div(
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justify-content": "space-between",
                                        "marginTop": "15px",
                                        "width": "99%",
                                        "marginLeft": "auto",
                                        "marginRight": "auto",
                                        "marginBottom": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    "Chart",
                                                    id="input-chart-btn",
                                                    className="toggle-btn active",
                                                    n_clicks=0,
                                                    style={
                                                        "flex": "1",
                                                        "padding": "5px",
                                                        "cursor": "pointer",
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                        "justifyContent": "center",
                                                        "backgroundColor": "#EBF3FF",
                                                        "color": "#1B69D0",
                                                        "border": "1px solid #1B69D0",
                                                        "borderTopLeftRadius": "10px",
                                                        "borderBottomLeftRadius": "10px",
                                                        "fontSize": "14px",
                                                    },
                                                ),
                                                html.Div(
                                                    "Table",
                                                    id="input-table-btn",
                                                    className="toggle-btn",
                                                    n_clicks=0,
                                                    style={
                                                        "fontSize": "14px",
                                                        "flex": "1",
                                                        "padding": "5px",
                                                        "cursor": "pointer",
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                        "justifyContent": "center",
                                                        "textAlign": "center",
                                                        "backgroundColor": "#F3F4F6",
                                                        "border": "1px solid #9CA4AF",
                                                        "borderLeft": "none",
                                                        "borderTopRightRadius": "10px",
                                                        "borderBottomRightRadius": "10px",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "width": "178px",
                                                "height": "35px",
                                                "border": "none",
                                                "borderRadius": "10px",
                                                "overflow": "hidden",
                                            },
                                        ),
                                        html.Div(
                                            id="table-options-container",
                                            style={
                                                "display": "flex",
                                                "gap": "10px",
                                                "align-items": "center",
                                                "marginTop": "10px",
                                            },
                                            children=[
                                                html.Button(
                                                    "Save",
                                                    id="save-excel-btn",
                                                    n_clicks=0,
                                                    style={
                                                        "margin": 0,
                                                        "width": "100px",
                                                        "height": "35px",
                                                        "padding": "5px",
                                                        "border-radius": "10px",
                                                        "background-color": "#EBF3FF",
                                                        "border": "1px solid #C4DAF7",
                                                    },
                                                ),
                                                html.Div(id="save-status"),
                                                html.Button(
                                                    "Edit",
                                                    id="edit-table-btn",
                                                    n_clicks=0,
                                                    style={
                                                        "margin": 0,
                                                        "width": "150px",
                                                        "height": "35px",
                                                        "padding": "5px",
                                                        "border-radius": "10px",
                                                        "background-color": "#134A94",
                                                        "color": "white",
                                                        "border": "none",
                                                    },
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                # graph
                                dcc.Graph(
                                    id="input-model-results-graph",
                                    style={
                                        "height": "37vh",
                                        "margin": 0,
                                        "marginTop": "10px",
                                        "padding": 0,
                                    },
                                ),
                                # table
                                html.Div(
                                    id="table-container",style={
                                        "display" : "none",
                                    },
                                ),
                            ],
                        ),
                        html.Button(
                            "Go to Run Model",
                            id="run-model-redirect-button",
                            n_clicks=0,
                            style={
                                "marginTop": "10px",
                                "width": "200px",
                                "height": "35px",
                                "padding": "5px",
                                "border-radius": "10px",
                                "background-color": "#EBF3FF",
                                "border": "1px solid #C4DAF7",
                                "fontWeight": "550",
                            },
                        ),
                    ],
                ),
            ],
        ),
        dcc.Store(id="stored-sheets-data"),
        dcc.Store(id="active-sheet-name"),
        dcc.Download(id="download-excel-sheets"),
        stellar_notification,
    ],
)


dialog_lock = threading.Lock()


def open_input_excel_file_dialog(result_queue):
    """Function to open file dialog and send the result back using a queue."""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xls;*.xlsx")], parent=root
        )

        result_queue.put(file_path)
    except Exception as e:
        result_queue.put(f"Error: {str(e)}")
    finally:
        try:
            root.destroy()
        except:
            pass


def select_input_file():
    """Opens file dialog in a separate thread and returns the selected file path."""
    # Try to acquire the lock, return None if already locked
    if not dialog_lock.acquire(blocking=False):
        # print("File dialog is already open", file=sys.stderr)
        return None

    result_queue = queue.Queue()

    try:
        # Create and start thread
        dialog_thread = threading.Thread(
            target=open_input_excel_file_dialog, args=(result_queue,), daemon=True
        )
        dialog_thread.start()

        # Wait for the result
        try:
            result = result_queue.get(timeout=300)  # 5 minute timeout
            if isinstance(result, str) and result.startswith("Error:"):
                # print(f"File dialog error: {result}", file=sys.stderr)
                return None
            return result
        except queue.Empty:
            # print("File dialog timed out", file=sys.stderr)
            return None
        finally:
            # Ensure thread cleanup
            dialog_thread.join(timeout=1.0)
    finally:
        # Always release the lock
        dialog_lock.release()


def register_callbacks(app):

    @app.callback(
        Output("url", "href", allow_duplicate=True),
        Input("upload-input-file-btn", "n_clicks"),
        State("url", "href"),
        prevent_initial_call=True,
    )
    def update_input_file_url(n_clicks, current_url):
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
        input_file_path = select_input_file()
        if input_file_path:
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            query_params["input_file"] = [input_file_path]
            new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{urlencode(query_params, doseq=True)}"
            return new_url
        raise PreventUpdate

    @app.callback(
        Output("selected-input-file-path", "children"),
        Output("input-dashbaord-sheet-selector", "style"),
        Output("input-dashbaord-sidebar", "style"),
        Output("stored-sheets-data", "data"),
        Output("input-dashbaord-sheet-selector", "children"),
        Output("active-sheet-name", "data"),
        Output("input-dashboard-container", "style"),
        Output("input-dashboard-topbar", "style"),
        Output("input-dashbaord-sidebar", "children"),
        Output("input-content-container", "style"),
        Input("url", "href"),
    )
    def update_input_dashbaord_layout(
        current_url,
    ):
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        global file_path

        input_content_container_style = {"display": "none"}

        sidebar_style = {
            "backgroundColor": "#E6F0F9",
            "height": "100vh",
            "width": "13vw",
            "position": "absolute",
            "bottom": 0,
            "left": 0,
            "border": "none",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "borderRight": "1px solid #D1D5DB",
        }

        sheet_selector_style = {"display": "none"}

        input_dashboard_style = {
            "position": "absolute",
            "top": "10vh",
            "left": "13vw",
            "width": "calc(100vw - 13vw)",
            "height": "calc(87vh - 0vh)",
        }

        topbar_style = {
            "backgroundColor": "#FFFFFF",
            "height": "10vh",
            "width": "87vw",
            "position": "absolute",
            "top": 0,
            "right": 0,
            "border": "1px solid #D1D5DB",
            "display": "flex",
            "align-items": "center",
        }

        if "input_file" in query_params:
            input_file_path = query_params["input_file"][0]
            file_path = input_file_path

            if input_file_path:
                sidebar_style = {
                    "backgroundColor": "#E6F0F9",
                    "height": "100vh",
                    "width": "6vw",
                    "position": "absolute",
                    "bottom": 0,
                    "left": 0,
                    "border": "none",
                    "borderRight": "1px solid #D1D5DB",
                }

                sheet_selector_style = {
                    "backgroundColor": "#FFFFFF",
                    "width": "15vw",
                    "maxWidth": "215px",
                    "position": "absolute",
                    "bottom": 0,
                    "left": "6vw",
                    "top": "10vh",
                    "border": "1px solid #D1D5DB",
                    "overflowY": "auto",
                    "padding-top": "10px",
                }

                input_dashboard_style = {
                    "flexGrow": 1,
                    "position": "absolute",
                    "top": "10vh",
                    "left": "calc(6vw + 215px)",
                    "width": "calc(94vw - 215px)",
                    "height": "calc(87vh - 0vh)",
                    "display": "flex",
                    "flexDirection": "column",
                }

                topbar_style = {
                    "backgroundColor": "#FFFFFF",
                    "height": "10vh",
                    "width": "94vw",
                    "position": "absolute",
                    "top": 0,
                    "right": 0,
                    "border": "1px solid #D1D5DB",
                    "display": "flex",
                    "align-items": "center",
                }

                input_content_container_style = {
                    "flexGrow": 1,
                    "width": "95%",
                    "borderRadius": "10px",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                    "display": "flex",
                    "flex-direction": "column",
                    "gap": "7px",
                    "margin-top": "20px",
                    "margin-bottom": "20px",
                }

                try:
                    xl = pd.ExcelFile(input_file_path)
                    sheet_names = xl.sheet_names

                    dashboard_sheets = [
                        "Demand"
                    ]

                    ordered_sheets = [sheet for sheet in dashboard_sheets if sheet in sheet_names]
                    remaining_sheets = [sheet for sheet in sheet_names if sheet not in ordered_sheets]

                    sheet_names = ordered_sheets + remaining_sheets

                    sheets_data = {}
                    for sheet in sheet_names:
                        df = xl.parse(sheet)
                        sheets_data[sheet] = df.to_json(
                            orient="split", date_format="iso"
                        )

                    active_sheet = sheet_names[0] if sheet_names else None

                    sheet_tabs = html.Div(
                        [
                            html.H3(
                                "Select Sheet",
                                style={
                                    "margin": "0 0 10px 0",
                                    "padding": "5px",
                                    "color": "#0F3B75",
                                },
                            )
                        ]
                        + [
                            html.Button(
                                sheet_name,
                                id={"type": "sheet-button", "index": i},
                                style={
                                    "padding": "10px",
                                    "width": "100%",
                                    "border": "none",
                                    "cursor": "pointer",
                                    "marginBottom": "5px",
                                    "textAlign": "left",
                                    "borderRadius": "10px",
                                    "backgroundColor": (
                                        "#C4DAF7"
                                        if sheet_name == active_sheet
                                        else "white"
                                    ),
                                    "color": (
                                        "#0F3B75"
                                        if sheet_name == active_sheet
                                        else "black"
                                    ),
                                },
                            )
                            for i, sheet_name in enumerate(sheet_names)
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "padding": "10px",
                            "paddingTop": "5px",
                        },
                    )

                    return (
                        f"{input_file_path}",
                        sheet_selector_style,
                        sidebar_style,
                        sheets_data,
                        sheet_tabs,
                        active_sheet,
                        input_dashboard_style,
                        topbar_style,
                        compressed_sidebar_children,
                        input_content_container_style,
                    )

                except Exception as e:
                    # print(e)
                    return (
                        f"{input_file_path}",
                        sheet_selector_style,
                        sidebar_style,
                        None,
                        html.Div([f"Error processing file: {str(e)}"]),
                        None,
                        input_dashboard_style,
                        topbar_style,
                        sidebar_children,
                        input_content_container_style,
                    )

        return (
            "Upload Input File",
            {"display": "none"},
            sidebar_style,
            None,
            [],
            None,
            input_dashboard_style,
            topbar_style,
            sidebar_children,
            input_content_container_style,
        )

    @app.callback(
        Output("input-model-results-graph", "figure", allow_duplicate=True),    
        Output("input-model-results-graph", "style"),
        Output("table-container", "style"),
        Output("input-chart-btn", "style"),
        Output("input-table-btn", "style"),
        Output("input-filter-area", "style"),
        Output("table-options-container", "style"),
        [Input("input-chart-btn", "n_clicks"), Input("input-table-btn", "n_clicks")],
        State("input-model-results-graph", "figure"), 
        prevent_initial_call=True
    )
    def update_content_from_selector(chart_clicks, table_clicks, fig):

        if not fig or fig == {}:
            fig = go.Figure()
            fig.update_layout(
            autosize=True,
            margin=dict(l=20, r=20, t=50, b=5),
            height=None,
            width=None,
        )

        chart_style = {
            "flex": "1",
            "padding": "5px",
            "cursor": "pointer",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "textAlign": "center",
            "backgroundColor": "#EBF3FF",
            "color": "#1B69D0",
            "border": "1px solid #1B69D0",
            "borderTopLeftRadius": "10px",
            "borderBottomLeftRadius": "10px",
            "fontSize": "14px",
        }
        table_style = {
            "fontSize": "14px",
            "flex": "1",
            "padding": "5px",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "cursor": "pointer",
            "textAlign": "center",
            "backgroundColor": "#F3F4F6",
            "border": "1px solid #9CA4AF",
            "borderTopRightRadius": "10px",
            "borderBottomRightRadius": "10px",
        }

        filter_style = {
            "display": "flex",
            "alignItems": "center",
            "gap": "10px",
            "margin": 0,
            "marginLeft": "5px",
        }

        table_options_style = {
            "display": "flex",
            "gap": "10px",
            "align-items": "center",
        }
        if chart_clicks > table_clicks:
            chart_style["backgroundColor"] = "#EBF3FF"
            chart_style["color"] = "#1B69D0"
            table_style["backgroundColor"] = "#F3F4F6"
            table_style["borderLeft"] = ("none",)
            table_style["color"] = "black"
            return (
                fig,
                {
                    "height": "37vh",
                    "margin": 0,
                    "marginTop": "10px",
                    "padding": 0,
                },
                {"display": "none"},
                chart_style,
                table_style,
                filter_style,
                {"display": "none"},
            )
        else:
            table_style["backgroundColor"] = "#EBF3FF"
            table_style["color"] = "#1B69D0"
            table_style["border"] = ("1px solid #1B69D0",)
            chart_style["border"] = ("1px solid #9CA4AF",)
            chart_style["borderRight"] = ("none",)
            chart_style["backgroundColor"] = "#F3F4F6"
            chart_style["color"] = "black"
            return (
                fig,
                {"display": "none"},
                {
                    "height": "35vh",
                    "margin": 0,
                    "padding": 0,
                },
                chart_style,
                table_style,
                {"display": "none"},
                table_options_style,
            )

    @app.callback(
        Output("active-sheet-name", "data", allow_duplicate=True),
        Output("input-dashbaord-sheet-selector", "children", allow_duplicate=True),
        [Input({"type": "sheet-button", "index": dash.dependencies.ALL}, "n_clicks")],
        [
            State("input-dashbaord-sheet-selector", "children"),
            State("active-sheet-name", "data"),
            State("stored-sheets-data", "data"),
        ],
        prevent_initial_call=True,
    )
    def set_active_sheet(n_clicks_list, sheet_tabs, current_active_sheet, sheets_data):
        ctx = dash.callback_context

        if not ctx.triggered or not sheets_data or not any(n_clicks_list):
            return current_active_sheet, sheet_tabs

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        try:
            button_index = eval(button_id)["index"]

            #sheet_names = list(sheets_data.keys())
            #sheet_name = sheet_names[button_index]
                # Define the desired order of sheets
            dashboard_sheets = [
               "Demand"
            ]

            # Get all sheet names from the data
            all_sheet_names = list(sheets_data.keys())

            # Create an ordered list of sheets
            ordered_sheets = [sheet for sheet in dashboard_sheets if sheet in all_sheet_names]
            remaining_sheets = [sheet for sheet in all_sheet_names if sheet not in ordered_sheets]
            
            # Combine the ordered sheets
            sheet_names = ordered_sheets + remaining_sheets

            # Select the sheet based on the ordered list
            sheet_name = sheet_names[button_index]
            updated_sheet_tabs = html.Div(
                [
                    html.H3(
                        "Select Sheet",
                        style={
                            "margin": "0 0 10px 0",
                            "padding": "5px",
                            "color": "#0F3B75",
                        },
                    )
                ]
                + [
                    html.Button(
                        name,
                        id={"type": "sheet-button", "index": i},
                        style={
                            "padding": "10px",
                            "width": "100%",
                            "border": "none",
                            "cursor": "pointer",
                            "marginBottom": "5px",
                            "textAlign": "left",
                            "borderRadius": "10px",
                            "backgroundColor": (
                                "#C4DAF7" if name == sheet_name else "white"
                            ),
                            "color": "#0F3B75" if name == sheet_name else "black",
                        },
                    )
                    for i, name in enumerate(sheet_names)
                ],
                style={"display": "flex", "flexDirection": "column", "padding": "10px"},
            )

            return sheet_name, updated_sheet_tabs

        except Exception as e:
            # print(f"Error setting active sheet: {e}")
            import traceback

            traceback.print_exc()
            return current_active_sheet, sheet_tabs

    @app.callback(
        Output("table-container", "children"),
        [Input("stored-sheets-data", "data"), Input("active-sheet-name", "data")],
    )
    def display_sheet_data(sheets_data, active_sheet):
        if not sheets_data or not active_sheet:
            return None

        try:
            sheet_data_json = sheets_data[active_sheet]
            json_buffer = StringIO(sheet_data_json)
            df = pd.read_json(json_buffer, orient="split")

            data_table = dash_table.DataTable(
                id="editable-table",
                columns=[
                    {"name": col, "id": col, "editable": False} for col in df.columns
                ],
                data=df.to_dict("records"),
                editable=False,
                style_table={
                    "overflowX": "auto",
                    "overflowY": "auto",
                    "height": "37vh",
                    "width": "97%",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                    "border": "1px solid #D1D5DB",
                    "padding": "10px",
                    "borderRadius": "10px",
                },
                style_cell={
                    "minWidth": "100px",
                    "width": "100px",
                    "maxWidth": "100px",
                    "height": "20px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "normal",
                    "textAlign": "left",
                    "padding": "4px",
                    "border": "1px solid #ddd",
                },
                style_header={
                    "backgroundColor": "#C4DAF7",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "padding": "4px",
                    "border": "1px solid #85B3EF",
                },
                style_data={
                    "border": "1px solid #ddd",
                },
                style_data_conditional=[
                    {
                        "if": {"state": "active"},  # Highlight active cell
                        "backgroundColor": "rgba(0, 116, 217, 0.3)",
                        "border": "1px solid rgb(0, 116, 217)",
                    },
                ],
            )
            return data_table

        except Exception as e:
            return html.Div([f"Error displaying sheet data: {str(e)}"])

    @app.callback(
        [
            Output("edit-modal", "style"),
            Output("modal-editable-table", "columns"),
            Output("modal-editable-table", "data"),
        ],
        [Input("edit-table-btn", "n_clicks")],
        [State("editable-table", "columns"), State("editable-table", "data")],
        prevent_initial_call=True,
    )
    def open_modal(n_clicks, columns, data):
        if n_clicks:
            editable_columns = []
            for col in columns:
                new_col = col.copy()
                new_col["editable"] = True
                editable_columns.append(new_col)

            return {"display": "block"}, editable_columns, data
        return no_update, no_update, no_update

    @app.callback(
        Output("edit-modal", "style", allow_duplicate=True),
        [Input("cancel-edit-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def close_modal(n_clicks):
        if n_clicks:
            return {"display": "none"}
        return no_update

    @app.callback(
        [
            Output("editable-table", "data"),
            Output("edit-modal", "style", allow_duplicate=True),
        ],
        [Input("save-table-btn", "n_clicks")],
        [State("modal-editable-table", "data")],
        prevent_initial_call=True,
    )
    def save_and_close(n_clicks, modal_data):
        if n_clicks:
            return modal_data, {"display": "none"}
        return no_update, no_update

    @app.callback(
        Output("stored-sheets-data", "data", allow_duplicate=True),
        [Input("save-table-btn", "n_clicks")],
        [
            State("modal-editable-table", "data"),
            State("stored-sheets-data", "data"),
            State("active-sheet-name", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_stored_data(n_clicks, modal_data, sheets_data, active_sheet):
        if n_clicks and sheets_data and active_sheet:
            updated_sheets_data = sheets_data.copy()
            updated_sheets_data[active_sheet] = pd.DataFrame(modal_data).to_json(
                orient="split"
            )
            return updated_sheets_data
        return no_update

    @app.callback(
        [Output("save-confirmation-modal", "style"), Output("modal-overlay", "style")],
        [
            Input("save-excel-btn", "n_clicks"),
            Input("close-save-modal", "n_clicks"),
            Input("confirm-save-btn", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(save_clicks, close_clicks, confirm_clicks):
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        modal_overlay_style = {
            "display": "none",
            "position": "fixed",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "backgroundColor": "rgba(0, 0, 0, 0.5)",
            "zIndex": "1000",
            "justifyContent": "center",
            "alignItems": "center",
        }

        modal_style = {
            "display": "none",
            "position": "fixed",
            "zIndex": "1001",
            "left": "50%",
            "top": "50%",
            "transform": "translate(-50%, -50%)",
        }

        if trigger_id == "save-excel-btn" and save_clicks and save_clicks > 0:
            modal_overlay_style["display"] = "flex"
            modal_style["display"] = "block"
        else:
            modal_overlay_style["display"] = "none"
            modal_style["display"] = "none"

        return modal_style, modal_overlay_style

    # Save process callback remains the same as in the previous implementation
    @app.callback(
        [
            Output("save-status", "children"),
            Output("selected-input-file-path", "children", allow_duplicate=True),
            Output("save-confirmation-modal", "style", allow_duplicate=True),
            Output("modal-overlay", "style", allow_duplicate=True),
        ],
        [Input("confirm-save-btn", "n_clicks")],
        [
            State("project-name", "value"),
            State("selected-input-file-path", "children"),
            State("stored-sheets-data", "data"),
        ],
        prevent_initial_call=True,
    )
    def save_excel_to_predetermined_location(
        n_clicks, project_name, input_directory, stored_sheets_data
    ):
        if not n_clicks:
            return no_update, no_update, no_update, no_update

        if not stored_sheets_data:
            return (
                html.Div("No data to save.", style={"color": "red"}),
                input_directory,
                {"display": "none"},
                {"display": "none"},
            )

        if not project_name:
            return (
                html.Div("Please enter a project name.", style={"color": "red"}),
                input_directory,
                {"display": "none"},
                {"display": "none"},
            )

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            if input_directory:
                input_dir = os.path.dirname(input_directory)
                input_filename = os.path.basename(input_directory)
                input_filename = os.path.splitext(input_filename)[0]
            else:
                input_dir = os.path.expanduser("~/Documents")
                input_filename = "data"

            output_filename = f"{project_name}_{input_filename}_{timestamp}.xlsx"
            output_path = os.path.join(input_dir, output_filename)

            with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
                for sheet_name, sheet_data_json in stored_sheets_data.items():
                    df = pd.read_json(StringIO(sheet_data_json), orient="split")
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]

                    for i, col in enumerate(df.columns):
                        column_len = max(
                            df[col].astype(str).map(len).max(), len(str(col))
                        )
                        worksheet.set_column(i, i, min(column_len + 2, 50))

            modal_overlay_style = {
                "display": "none",
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0, 0, 0, 0.5)",
                "zIndex": "1000",
                "justifyContent": "center",
                "alignItems": "center",
            }

            modal_style = {
                "display": "none",
                "position": "fixed",
                "zIndex": "1001",
                "left": "50%",
                "top": "50%",
                "transform": "translate(-50%, -50%)",
            }

            return (
                html.Div(
                    f"File saved successfully: {output_filename}",
                    style={"color": "green"},
                ),
                output_path,
                modal_style,
                modal_overlay_style,
            )

        except Exception as e:
            modal_overlay_style = {
                "display": "none",
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0, 0, 0, 0.5)",
                "zIndex": "1000",
                "justifyContent": "center",
                "alignItems": "center",
            }

            modal_style = {
                "display": "none",
                "position": "fixed",
                "zIndex": "1001",
                "left": "50%",
                "top": "50%",
                "transform": "translate(-50%, -50%)",
            }

            return (
                html.Div(f"Error saving file: {str(e)}", style={"color": "red"}),
                input_directory,
                modal_style,
                modal_overlay_style,
            )

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("url", "search", allow_duplicate=True),
        Input("run-model-redirect-button", "n_clicks"),
        State("project-name", "value"),
        State("selected-input-file-path", "children"),
        prevent_initial_call=True,
    )
    def redirect_to_run_model(n_clicks, project_name, input_directory):
        if not n_clicks or not input_directory:
            return no_update, no_update

        if not project_name:
            project_name = ""

        encoded_project_name = quote(project_name)
        encoded_input_directory = quote(input_directory)

        pathname = "/run-model"
        search = (
            f"?projectName={encoded_project_name}&inputFile={encoded_input_directory}"
        )

        return pathname, search

    @app.callback(
        Output("zone-selector-container", "style"),
        Output("tech-selector-container", "style"),
        Output("quarter-selector-container", "style"),
        Output("day-selector-container", "style"),
        Output("year-selector-container", "style"),
        Output("storage-selector-container", "style"),
        Output("plant-selector-container", "style"),
        Input("selected-sheet-store", "data"),
    )
    def update_dropdown_style(selected_sheet):
        hidden_filter_style = {"display": "none"}
        return (
            hidden_filter_style,
            hidden_filter_style,
            hidden_filter_style,
            hidden_filter_style,
            hidden_filter_style,
            hidden_filter_style,
            hidden_filter_style,
        )

    @app.callback(
        Output("input-model-results-graph", "figure"),
        Output("zone-selector-container", "style", allow_duplicate=True),
        Output("tech-selector-container", "style", allow_duplicate=True),
        Output("quarter-selector-container", "style", allow_duplicate=True),
        Output("day-selector-container", "style", allow_duplicate=True),
        Output("year-selector-container", "style", allow_duplicate=True),
        Output("storage-selector-container", "style", allow_duplicate=True),
        Output("plant-selector-container", "style", allow_duplicate=True),
        Output("zone-selector", "options"),
        Output("tech-selector", "options"),
        Output("quarter-selector", "options"),
        Output("day-selector", "options"),
        Output("year-selector", "options"),
        Output("storage-selector", "options"),
        Output("plant-selector", "options"),
        Output("zone-selector", "multi"),
        Output("quarter-selector", "multi"),
        Output("day-selector", "multi"),
        Output("year-selector", "multi"),
        Output("zone-selector", "value"),
        Output("quarter-selector", "value"),
        Output("day-selector", "value"),
        Output("year-selector", "value"),
        Input("active-sheet-name", "data"),
        Input("zone-selector", "value"),
        Input("tech-selector", "value"),
        Input("quarter-selector", "value"),
        Input("day-selector", "value"),
        Input("year-selector", "value"),
        Input("storage-selector", "value"),
        Input("plant-selector", "value"),
        prevent_initial_call=True,
    )
    def update_input_dashboard(
        selected_sheet_name,
        selected_zones,
        selected_techs,
        selected_quarters,
        selected_days,
        selected_years,
        selected_storage,
        selected_plants,
    ):

        visual_filter_style = {
            "display": "block",
            "width": "10vw",
            "height": "38px",  # Fixed height for the container
            "overflow": "visible",  # Allow dropdown menu to expand outside the container
            "zIndex": 1,
            # "borderRadius": "10px",
        }
        hidden_filter_style = {"display": "none"}

        fig = go.Figure()
        zone_style = hidden_filter_style
        tech_style = hidden_filter_style
        quarter_style = hidden_filter_style
        day_style = hidden_filter_style
        year_style = hidden_filter_style
        storage_style = hidden_filter_style
        plant_style = hidden_filter_style

        zone_options = []
        tech_options = []
        quarter_options = []
        day_options = []
        year_options = []
        storage_options = []
        plant_options = []

        zone_multi = False
        quarter_multi = False
        day_multi = False
        year_multi = False

        # zone_values = []
        # quarter_values = []
        # day_values = []
        # year_values = []

        if (
            selected_sheet_name == "MustRunTrajectoryMax"
            or selected_sheet_name == "MustRunTrajectoryMin"
        ):

            # preprocessing data
            (
                mustrun_max_df,
                mustrun_min_df,
                years_max,
                years_min,
                zones,
                technologies,
            ) = preprocess_mustrun_trajectory()

            zone_options = [{"label": zone, "value": zone} for zone in zones]
            tech_options = [{"label": tech, "value": tech} for tech in technologies]

            if selected_sheet_name == "MustRunTrajectoryMax":
                traj_type = "Max"
            else:
                traj_type = "Min"

            # Choose the correct dataset
            if traj_type == "Max":
                title_text = "Yearly max capacity additions possible for MustRun Technologies in MW"
                selected_df = mustrun_max_df.copy()
                y_axis_label = "Max Capacity Addition (MW)"
                selected_years = years_max
            else:
                title_text = "Yearly min capacity additions for MustRun Technologies in MW"
                selected_df = mustrun_min_df.copy()
                y_axis_label = "Min Capacity Addition (MW)"
                selected_years = years_min

            filtered_df = selected_df.copy()
            if selected_zones != "All":
                filtered_df = filtered_df[filtered_df["Zone"] == selected_zones]
            if selected_techs != "All":
                filtered_df = filtered_df[filtered_df["Technology"] == selected_techs]

            filtered_df = filtered_df.dropna(axis=1, how="all")

            existing_years = [
                col for col in selected_years if col in filtered_df.columns
            ]

            zone_style = visual_filter_style
            tech_style = visual_filter_style

            if existing_years:
                summary_df = (
                    filtered_df.groupby("Technology")[existing_years]
                    .sum()
                    .reset_index()
                )
                summary_df[existing_years] = (
                    summary_df[existing_years].round(0).astype(int)
                )

                fig = go.Figure()
                for _, row in summary_df.iterrows():
                    fig.add_trace(
                        go.Scatter(
                            x=existing_years,
                            y=row[existing_years],
                            mode="lines+markers",
                            name=row["Technology"],
                        )
                    )

                fig.update_layout(
                    title=title_text,
                    xaxis_title="Year",
                    yaxis_title=y_axis_label,
                    legend_title="Technology",
                    font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                )

        elif (
            selected_sheet_name == "MustRunTrajectoryStateMax"
            or selected_sheet_name == "MustRunTrajectoryStateMin"
        ):
            if selected_sheet_name == "MustRunTrajectoryStateMax":
                traj_type = "StateMax"
            else:
                traj_type = "StateMin"

            state_max_df, years_state_max = preprocess_mustrun_trajectory_state(
                "MustRunTrajectoryStateMax"
            )
            state_min_df, years_state_min = preprocess_mustrun_trajectory_state(
                "MustRunTrajectoryStateMin"
            )

            if traj_type == "StateMax":
                title_text = "Maximum capacity achievable for MustRun Technologies in MW"
                selected_df = state_max_df.copy()
                y_axis_label = "Capacity (MW)"
                selected_years = years_state_max
            else:
                title_text = "Minimum capacity targets for MustRun Technologies in MW"
                selected_df = state_min_df.copy()
                y_axis_label = "Capacity targets (MW)"
                selected_years = years_state_min

            if not selected_df.empty and selected_years:
                existing_years = [
                    col for col in selected_years if col in selected_df.columns
                ]

                if existing_years:

                    summary_df = (
                        selected_df.groupby("Technology")[existing_years]
                        .sum()
                        .reset_index()
                    )
                    summary_df[existing_years] = (
                        summary_df[existing_years].round(0).astype(int)
                    )

                    fig = go.Figure()
                    for _, row in summary_df.iterrows():
                        fig.add_trace(
                            go.Scatter(
                                x=existing_years,
                                y=row[existing_years],
                                mode="lines+markers",
                                name=row["Technology"],
                            )
                        )

                    fig.update_layout(
                        title=title_text,
                        xaxis_title="Year",
                        yaxis_title=y_axis_label,
                        legend_title="Technology",
                        font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                    )

        elif (
            selected_sheet_name == "Demand" or selected_sheet_name == "MustRunProfiles" or selected_sheet_name == "DemandProfile"
        ):
            
            if selected_sheet_name == "Demand":
                title_text ="Demand in MW" 
                y_axis_label = ("Demand (MW)")
            elif selected_sheet_name == "DemandProfile":
                title_text ="Demand profiles - Normalized by peak" 
                y_axis_label = ("Fraction of the Peak")
            else:
                title_text ="RE profiles - CUF - Fraction of Capacity" 
                y_axis_label = ("CUF") 

            name_format = (
                "{zone} - {quarter} - {day} - {year}"
                if selected_sheet_name == "Demand"
                else "{zone} - {quarter} - {day}"
            )
            zone_col = "Zone" if selected_sheet_name == "Demand" or selected_sheet_name == "DemandProfile" else "PlantName"

            entire_df = pd.read_excel(
                file_path, sheet_name=selected_sheet_name, skiprows=4
            )
            df = entire_df

            zone_options = [
                {"label": z, "value": z} for z in entire_df[zone_col].dropna().unique()
            ]
            quarter_options = [
                {"label": q, "value": q} for q in entire_df["Quarter"].dropna().unique()
            ]
            day_options = [
                {"label": d, "value": d} for d in entire_df["Day"].dropna().unique()
            ]
            if selected_sheet_name == "Demand":
                year_options = (
                    [{"label": y, "value": y} for y in entire_df["Year"].dropna().unique()]
                    if "Year" in entire_df.columns
                    else []
                )

                if not selected_zones:
                    selected_zones = []
                    selected_zones.append(zone_options[0]["value"])  

                if not selected_quarters:
                    selected_quarters = []
                    selected_quarters.append(quarter_options[0]["value"])      

                if not selected_days:
                    selected_days = []
                    selected_days.append(day_options[0]["value"])      

                if not selected_years:
                    selected_years = []
                    selected_years.append(year_options[0]["value"])      

            if selected_zones:
                df = df[df[zone_col].isin(selected_zones)]
            if selected_plants:
                df = df[df[zone_col].isin(selected_plants)]    
            if selected_quarters:
                df = df[df["Quarter"].isin(selected_quarters)]
            if selected_days:
                df = df[df["Day"].isin(selected_days)]
            if selected_years and "Year" in df.columns:
                df = df[df["Year"].isin(selected_years)]

            timeblocks = [f"t{i}" for i in range(1, 25)]
            fig = go.Figure()
            for _, row in df.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=timeblocks,
                        y=row[timeblocks].values,
                        mode="lines+markers",
                        name=name_format.format(
                            zone=row[zone_col],
                            quarter=row["Quarter"],
                            day=row["Day"],
                            year=row["Year"] if "Year" in df.columns else "",
                        ).strip(" -"),
                    )
                )
            fig.update_layout(
                title=title_text,
                xaxis_title="Timeblocks",
                yaxis_title=y_axis_label,
                template="plotly_white",
                font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
            )

            zone_style = visual_filter_style
            quarter_style = visual_filter_style
            day_style = visual_filter_style
            if selected_sheet_name == "Demand":
                year_style = visual_filter_style
            if selected_sheet_name == "MustRunProfiles":    
                plant_style = visual_filter_style
                zone_style = hidden_filter_style
                plant_options = zone_options
            zone_multi = True
            quarter_multi = True
            day_multi = True
            year_multi = True

        elif selected_sheet_name == "RPO":
            df = get_rpo_data()
            for col in df.columns:
                if col != "Year":
                    fig.add_trace(
                        go.Scatter(
                            x=df.index, y=df[col], mode="lines+markers", name=col
                        )
                    )
                    fig.update_layout(title="RPO targets",yaxis_title="RPO Targets (%)", xaxis_title="Year",
                                      font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                                      )
        elif selected_sheet_name == "Thermal":
            thermal_index_df = get_mappings(
                "Index", [4, 5], ["Fuel Type", "Fuel Index"]
            )
            df = get_thermal_data(thermal_index_df)
            for col in df.columns[1:]:
                fig.add_trace(go.Bar(x=df.iloc[:, 0], y=df[col], name=col))
            fig.update_layout(title="Thermal Capacities - Existing and Planned - in MW",yaxis_title="Capacity (MW)", xaxis_title=df.columns[0],
                              font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    ))
        elif selected_sheet_name == "Hydro":
            hydro_index_df = get_mappings(
                "Index", [14, 15], ["Fuel Type", "Type Index"]
            )
            df = get_hydro_data(hydro_index_df)
            for col in df.columns[1:]:
                fig.add_trace(go.Bar(x=df.iloc[:, 0], y=df[col], name=col))
            fig.update_layout(title="Hydro Capacities - Existing and Planned - in MW",yaxis_title="Capacity (MW)", xaxis_title=df.columns[0],
                              font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                              )
        elif selected_sheet_name == "MustRun":
            must_run_index_df = get_mappings(
                "Index", [8, 9], ["Technology", "Type Index"]
            )
            df = get_must_run_data(must_run_index_df)
            for col in df.columns[1:]:
                fig.add_trace(go.Bar(x=df.iloc[:, 0], y=df[col], name=col))
            fig.update_layout(title="MustRun Capacities in MW",yaxis_title="Capacity (MW)", xaxis_title=df.columns[0],
                              font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                              )
        elif selected_sheet_name == "MinimumStorageTargets":
            df = get_storage_targets_data()

            # Clean and reshape
            df.rename(columns={df.columns[0]: "Technology"}, inplace=True)
            df.columns = df.columns.astype(str)
            df.dropna(axis=1, how="all", inplace=True)

            # Extract year columns
            years = [col for col in df.columns[1:] if col.isdigit()]

            # Ensure numeric and clean
            for col in years:
                df[col] = pd.to_numeric(df[col], errors="coerce").round(0).astype("Int64")

            # Melt into long format: Technology | Year | Capacity
            df_long = df.melt(id_vars="Technology", value_vars=years, 
                            var_name="Year", value_name="Capacity")

            # Plot using lines
            fig = go.Figure()

            for tech in df_long["Technology"].unique():
                tech_data = df_long[df_long["Technology"] == tech]
                fig.add_trace(go.Scatter(
                    x=tech_data["Year"],
                    y=tech_data["Capacity"],
                    mode='lines+markers',
                    name=tech
                ))

            # Update layout
            fig.update_layout(
                title="Targets for storage technologies in MW",
                xaxis_title="Year",
                yaxis_title="Capacity (MW)",
                template="plotly_white",
                font=dict(family="Arial", size=20, color="black"),
                title_font=dict(size=25, color='black'),
                xaxis=dict(title_font=dict(size=20), tickfont=dict(size=20)),
                yaxis=dict(title_font=dict(size=20), tickfont=dict(size=20)),
                legend=dict(title_font=dict(size=20), font=dict(size=20))
            )


        elif selected_sheet_name == "Storage":
            storage_index_df = get_mappings(
                "Index", [11, 12], ["Storage Technology", "Type Index"]
            )
            df = get_storage_data(storage_index_df)
            storage_options = [
                {"label": "Energy Capacity (MW)", "value": "Energy Capacity (MW)"},
                {"label": "Energy Storage (MWh)", "value": "Energy Storage (MWh)"},
            ]

            if selected_storage == "Energy Capacity (MW)":
                for col in df.columns[1:3]:
                    fig.add_trace(go.Bar(x=df.iloc[:, 0], y=df[col], name=col))

                fig.update_layout(
                    title="Existing and planned storage Capacity (MW)",
                    yaxis_title="Capacity (MW)",
                    xaxis_title=df.columns[0],
                    font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                )

            if selected_storage == "Energy Storage (MWh)":
                for col in df.columns[3:5]:
                    fig.add_trace(go.Bar(x=df.iloc[:, 0], y=df[col], name=col))

                fig.update_layout(
                    title="Existing and planned storage Capacity (MWh)",
                    yaxis_title="Storage Capacity (MWh)",
                    xaxis_title=df.columns[0],
                    font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
                )

            storage_style = visual_filter_style

        elif selected_sheet_name == "Demand_freq_dist":
            fig, data, columns = process_demand_frequency(file_path)

        elif selected_sheet_name == "Demand_freq_variation":
            fig, data, columns = process_demand_frequency_variation(file_path)    

        fig.update_layout(
            autosize=True,
            margin=dict(l=20, r=20, t=50, b=5),
            height=None,
            width=None,
            font=dict(
                    family="Arial",  # or any font you prefer
                    size=20,        # base font size
                    color="black"
                    ),
                    # Title font settings
                    title_font=dict(
                        size=25,
                        color='black'
                    ),
                    # Axis titles
                    xaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20),
                    ),
                    yaxis=dict(
                        title_font=dict(size=20),
                        tickfont=dict(size=20)
                    ),
                    # Legend font settings
                    legend=dict(
                        title_font=dict(size=20),
                        font=dict(size=20)
                    )
        )

        return (
            fig,
            zone_style,
            tech_style,
            quarter_style,
            day_style,
            year_style,
            storage_style,
            plant_style,
            zone_options,
            tech_options,
            quarter_options,
            day_options,
            year_options,
            storage_options,
            plant_options,
            zone_multi,
            quarter_multi,
            day_multi,
            year_multi,
            selected_zones,
            selected_quarters,
            selected_days,
            selected_years
        )

        # raise PreventUpdate
