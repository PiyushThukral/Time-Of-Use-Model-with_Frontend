from dash import html, dcc, Output, Input, callback, Dash
from steps_module import step_upload_data, step_select_output_folder #, step_visualize_data
import dash
import plotly.graph_objs as go

# Layout
layout = html.Div(
    style={"display": "flex", "height": "100vh", "fontFamily": "Inter, sans-serif"},
    children=[
        dcc.Store(id="store-uploaded-file", storage_type="session"),
        # Left Panel – Step-by-step guide placeholder
        html.Div(
            style={
                "flex": "1",
                "padding": "20px",
                "backgroundColor": "#F9FAFB",
                "borderRight": "1px solid #E5E7EB",
                "overflowY": "auto"
            },
            children=[
                #html.H3("Steps Panel", style={"marginBottom": "20px"}),
                #html.P("This panel will later contain steps such as upload, settings, visualization, etc.")
                step_upload_data(),
                step_select_output_folder(),
                #step_visualize_data(),
                dcc.Store(id="store-uploaded-file"),
            ]
        ),

        # Right Panel – Divided into 3 sections: logo, graph area, logs
        html.Div(
            style={"flex": "3", "display": "flex", "flexDirection": "column", "padding": "20px"},
            children=[

                # Top: Logo
                html.Div(
                    id="logo-area",
                    style={
                        "height": "80px",
                        "marginBottom": "10px",
                        "display": "flex",
                        "justifyContent": "flex-end",
                        "alignItems": "center"
                    },
                    children=[
                        html.Img(src="/assets/MoP logo.png", style={"height": "60px"})
                    ]
                ),

                # Middle: Interactive visualization area
                html.Div(
                    id="visualization-area",
                    style={
                        "flex": "1",
                        "backgroundColor": "#FFFFFF",
                        "border": "1px solid #E5E7EB",
                        "borderRadius": "10px",
                        "padding": "20px",
                        "marginBottom": "10px",
                        "overflowY": "auto"
                    },
                    children=[
                        #dcc.Graph(id='input-data-graph', style={'height': '400px'}),
                        html.P("Interactive charts or outputs will appear here.")
                    ]
                ),

                # Bottom: Logs area
                html.Div(
                    id="logs-area",
                    style={
                        "height": "150px",
                        "backgroundColor": "#F3F4F6",
                        "border": "1px solid #D1D5DB",
                        "borderRadius": "10px",
                        "padding": "10px",
                        "fontSize": "13px",
                        "overflowY": "scroll",
                        "whiteSpace": "pre-line"
                    },
                    children=[
                        html.P("Logs will appear here...")
                    ]
                )
            ]
        )
    ]
)



import tkinter as tk
from tkinter import filedialog
import threading
import queue

dialog_lock = threading.Lock()

def open_output_folder_dialog(result_queue):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        folder_path = filedialog.askdirectory(parent=root)

        result_queue.put(folder_path)
    except Exception as e:
        result_queue.put(f"Error: {str(e)}")
    finally:
        try:
            root.destroy()
        except:
            pass


def select_output_directory():
    if not dialog_lock.acquire(blocking=False):
        return None

    result_queue = queue.Queue()

    try:
        dialog_thread = threading.Thread(
            target=open_output_folder_dialog, args=(result_queue,), daemon=True
        )
        dialog_thread.start()

        try:
            result = result_queue.get(timeout=300)
            if isinstance(result, str) and result.startswith("Error:"):
                return None
            return result
        except queue.Empty:
            return None
        finally:
            dialog_thread.join(timeout=1.0)
    finally:
        dialog_lock.release()

from dash import Input, Output, State, callback, no_update
from dash import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import base64
import io

import base64
import io
import pandas as pd

import pandas as pd
import os

from pages.cache import inputfileDirCache

def get_scenario_df():
    
    fp = inputfileDirCache.get()  # this must return the full path to the uploaded file

    if os.path.exists(fp):
        df = pd.read_excel(
            fp,
            parse_dates=["Date"]
        )
        df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
        return df

    return None


def register_callbacks(app):
    @app.callback(
        Output("store-uploaded-file", "data"),
        Output("file-upload-status", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def handle_file_upload(contents, filename):
        if contents and filename:
            file_path = os.path.join("temp_data", filename)
            os.makedirs("temp_data", exist_ok=True)
            data = {"filename": filename, "contents": contents}
            status = f"✅ File selected: {filename}"
            inputfileDirCache.set(file_path) 
            return data, status
        else:
            return no_update, ""
            

    @app.callback(
        Output("selected-folder-path", "children"),
        Output("output-folder-store", "data"),
        Input("select-folder-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def on_select_folder(n_clicks):
        folder_path = select_output_directory()
        if folder_path:
            return f"Selected folder: {folder_path}", folder_path
        else:
            return "No folder selected or dialog cancelled.", None
    
