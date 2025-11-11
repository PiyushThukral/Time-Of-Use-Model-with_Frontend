from dash import html, dcc, Output, Input, callback, Dash
from steps_module import step_upload_data, step_select_output_folder , step_render_graph , step_select_tou_dynamicity, select_tou_bins, first_last_continuity, step_upload_model_param, step_run_model, step_view_results, view_customer_profile
import dash
import plotly.graph_objs as go
from pages.cache import inputfileDirCache , SaveDirCache , ToUDynamicityCache , RepProfileCache , model_param_Cache ,OutputFileNameCache
import sys
from sklearn.ensemble import IsolationForest
import pages
from dash import Input, Output, State, callback, no_update
from dash import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import base64
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import threading
import io
import sys

log_buffer = io.StringIO()
model_thread = None
model_running = False


from pages import new_betrand_VM

def load_cached_df():
    fp = inputfileDirCache.get()

    if not fp or not os.path.exists(fp):
        #print("Invalid or missing file path.")
        raise PreventUpdate

    print(f"Trying to load file: {fp}")
    try:
        if fp.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(fp)
            #print("Loaded as Excel.")
        elif fp.lower().endswith('.csv'):
            df = pd.read_csv(fp)
            #print("Loaded as CSV.")
        else:
            raise ValueError("Unsupported file type.")
    except Exception as e:
        #print(f"Failed to load file: {e}")
        raise PreventUpdate

    # Handle Date column
    if 'Date' not in df.columns:
        #print("Missing 'Date' column.")
        raise PreventUpdate

    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
    except Exception as e:
        #print(f"Failed to parse 'Date' column: {e}")
        raise PreventUpdate

    return df

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
                #step_render_graph(),
                #step_select_tou_dynamicity(),
                #step_select_representative_profile(),
                select_tou_bins(),
                first_last_continuity(),
                step_upload_model_param(),
                step_run_model(),
                step_view_results(),
                dcc.Store(id="store-uploaded-file"),
                dcc.Store(id="selected-hours-store", storage_type="session"),
                dcc.Store(id = "continuity-setting", storage_type="session"),
                dcc.Store(id = "store-final-indiv-data", data =  {"data" : ""}, storage_type="session")
                #dcc.Store(id = "output-file-name-input", storage_type="session"),
            ]
        ),

        # Right Panel – Divided into 3 sections: logo, graph area, logs
        html.Div(
            style={"flex": "3", "display": "flex", "flexDirection": "column", "padding": "20px"},
            children=[

                # # Top: Logo
                # html.Div(
                #     id="logo-area",
                #     style={
                #         "height": "80px",
                #         "marginBottom": "10px",
                #         "display": "flex",
                #         "justifyContent": "flex-end",
                #         "alignItems": "center"
                #     },
                #     children=[
                #         html.Img(src="/assets/CEA logo.png", style={"height": "60px"})
                #     ]
                # ),

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
                        #html.P("Interactive charts or outputs will appear here.")
                        view_customer_profile()

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

    #############################
    ####### STEP 1 ############## READ INPUT FILE
    ############################# 

    @app.callback(
        Output("store-uploaded-file", "data"),
        Output("file-upload-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        #State("logs-area", "children"),
        prevent_initial_call=True,
    )
    def handle_file_upload(contents, filename):
        if not contents:
            raise PreventUpdate

        try:
            # Decode content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Save locally
            os.makedirs("temp_data", exist_ok=True)
            file_path = os.path.join("temp_data", filename)

            with open(file_path, "wb") as f:
                f.write(decoded)

            # Cache path for later use
            inputfileDirCache.set(file_path)

            # Store file data in memory (for later inspection or plotting)
            store_data = {
                "filename": filename,
                "path": file_path
            }

            return (
                store_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} saved to {file_path}"),
                #html.Div(f"✅ Use drop-downs to visualize")
            )

        except Exception as e:
            return (
                no_update,
                html.Div("❌ Upload failed."),
                html.Div(f"❌ Error: {str(e)}")
            )

    #############################
    ####### STEP 2 ############## SELECT OUTPUT DIRECTORY
    #############################    

    @app.callback(
        Output("selected-folder-path", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Output("output-folder-store", "data"),
        Input("select-output-folder-btn", "n_clicks"),
        #State("output-folder-input", "abs_path_folder"),
        prevent_initial_call=True
    )
    def on_select_folder(n_clicks):
        folder_path = select_output_directory()

        if not folder_path:
            return "❌ No folder selected or dialog cancelled.", html.Div("❌ No folder selected or dialog cancelled."), None

        try:
            os.makedirs(folder_path, exist_ok=True)
            abs_path = os.path.abspath(folder_path)
            SaveDirCache.set(abs_path)

            msg = f"✅ Output folder set to: {abs_path}"

            # abs_path_folder = {
            #     "output_path": abs_path,
            # }
            
            return msg, html.Div(msg), {"output_folder": abs_path}
        
        except Exception as e:
            err_msg = f"❌ Error setting folder: {str(e)}"
            return abs_path, err_msg, html.Div(err_msg), None
    
    #############################
    ####### STEP 2 ############## ENTER OUTPUT FILE NAME
    #############################   


    # @app.callback(
    #     Output("output-file-name-store", "data"),
    #     Output("output-file-name-log", "children"),
    #     Input("confirm-output-filename-btn", "n_clicks"),
    #     State("output-file-name-input", "value"),
    #     prevent_initial_call=True
    # )
    # def store_output_file_name(n_clicks, file_name):
    #     if not file_name:
    #         return no_update, "Please enter a valid output file name."

    #     cleaned_name = file_name.strip()
    #     OutputFileNameCache.set(cleaned_name)
    #     print(f"Output file name saved as: {cleaned_name}")
    #     return cleaned_name, f"Output file name saved as: {cleaned_name}"


    @app.callback(
        Output("output-file-name-store", "data"),
        Output("output-file-name-log", "children"),
        Input("confirm-output-filename-btn", "n_clicks"),
        State("output-file-name-input", "value"),
        prevent_initial_call=True
    )
    def store_output_file_name(n_clicks, file_name):
        if file_name:
            cleaned_name = file_name.strip()
            print("file_name_testing_ok")
            if not cleaned_name or cleaned_name.lower() in ['output', 'con', 'nul']:  # Windows reserved words
                return no_update, "⚠️ Please enter a valid output file name."
            print("file_cache_testing_ok")
            OutputFileNameCache.set(cleaned_name)
            return cleaned_name, f"✅ Output file name saved as: {cleaned_name}.xlsx"

        OutputFileNameCache.set(None)
        return "", "⚠️ Please enter a valid output file name."

    #############################
    ####### STEP 3 ############## VISUALIZE PLOTS
    #############################

    # @app.callback(
    #     Output("cat-dropdown", "options",allow_duplicate=True),
    #     Output("sanction-dropdown", "options",allow_duplicate=True),
    #     Output("cnumber-dropdown", "options",allow_duplicate=True),
    #     Output("logs-area", "children", allow_duplicate=True),
    #     Input("store-uploaded-file", "data"),
    #     prevent_initial_call=True
    # )
    # def populate_dropdowns(uploaded_file):
    #     try:
    #         # Get cached file path
    #         print("Testing....")
    #         fp = inputfileDirCache.get()  # full path to the uploaded file

    #         if not fp or not os.path.exists(fp):
    #             return [], [], [], html.Div("❌ File path is invalid or missing.")

    #         # Read Excel file
    #         df = pd.read_excel(fp, parse_dates=["Date"])
    #         df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')

    #         # Build dropdown options
    #         cat_options = [{"label": cat, "value": cat} for cat in sorted(df["Category"].dropna().unique())]
    #         sanction_options = [{"label": val, "value": val} for val in sorted(df["Sanctioned_Load_KW"].dropna().unique())]
    #         consumer_options = [{"label": str(cn), "value": str(cn)} for cn in sorted(df["Consumer No"].dropna().unique())]

    #         return cat_options, sanction_options, consumer_options, html.Div("✅ Dropdowns populated. Select drop-downs to view individual Consumer Profile")
        
    #     except Exception as e:
    #         return [], [], [], html.Div(f"❌ Dropdown error: {str(e)}")

    @app.callback(
        Output("cat-dropdown", "options",allow_duplicate=True),
        Input("store-uploaded-file", "data"),
        prevent_initial_call=True
    )
    def populate_cat_dropdowns(uploaded_file):
        try:
            # Get cached file path

            fp = inputfileDirCache.get()  # full path to the uploaded file
            df = load_cached_df()


            if not fp or not os.path.exists(fp):
                return []

            # Build dropdown options
            cat_options = [{"label": cat, "value": cat} for cat in sorted(df["Category"].dropna().unique())]

            return cat_options

        except Exception as e:
            return []
    #
    @app.callback(
        Output("sanction-dropdown", "options", allow_duplicate=True),
        Input("store-uploaded-file", "data"),
        Input("cat-dropdown", "value"),
        prevent_initial_call=True
    )
    def populate_sanction_load_dropdowns(uploaded_file, category):
        try:

            fp = inputfileDirCache.get()
            df = load_cached_df()
            if not fp or not os.path.exists(fp):
                return []

            # Filter if category is selected
            if category:
                df_sub = df[df['Category'] == category]

                # Generate sanction load options
                sanction_options = [
                    {"label": val, "value": val}
                    for val in sorted(df_sub["Sanctioned_Load_KW"].dropna().unique())
                ]

                if sanction_options:
                    return sanction_options
                else:
                    return []

            else:
                # Generate sanction load options
                sanction_options = [
                    {"label": val, "value": val}
                    for val in sorted(df["Sanctioned_Load_KW"].dropna().unique())
                ]

                if sanction_options:
                    return sanction_options
                else:
                    return []

        except Exception as e:
            return []

    @app.callback(
        Output("cnumber-dropdown", "options", allow_duplicate=True),
        Input("store-uploaded-file", "data"),
        Input("cat-dropdown", "value"),
        Input("sanction-dropdown", "value"),
        prevent_initial_call=True
    )
    def populate_cnumber_dropdowns(uploaded_file, category, sanction_load):
        try:
            # Get cached file path

            fp = inputfileDirCache.get()
            df = load_cached_df()
            if not fp or not os.path.exists(fp):
                return []

            # Read Excel file
            #df = pd.read_excel(fp, parse_dates=["Date"])
            #df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')

            # Apply filters dynamically
            filters = []
            if category:
                filters.append(df['Category'] == category)
            if sanction_load:
                filters.append(df['Sanctioned_Load_KW'] == sanction_load)

            if filters:
                mask = filters[0]
                for f in filters[1:]:
                    mask &= f
                df_sub = df[mask].copy()

                # Create dropdown options
                consumer_options = [
                    {"label": str(cn), "value": str(cn)}
                    for cn in sorted(df_sub["Consumer No"].dropna().unique())
                ]

                if consumer_options:
                    return consumer_options
                else:
                    return []

            else:
                consumer_options = [
                    {"label": str(cn), "value": str(cn)}
                    for cn in sorted(df["Consumer No"].dropna().unique())
                ]

                return consumer_options

        except Exception as e:
            return []


    @app.callback(
        Output("profile-graph", "figure",allow_duplicate=True),
        Input("cat-dropdown", "value"),
        Input("sanction-dropdown", "value"),
        Input("cnumber-dropdown", "value"),
        prevent_initial_call=True
    )


    def update_graph(category, sanctioned_load, consumer_no):
        #df = get_scenario_df()

        df = load_cached_df()

        # Ensure data exists and all filters are provided
        if df is None: # or not all([category, sanctioned_load, consumer_no]):
            raise dash.exceptions.PreventUpdate

        # # Filter data
        # filtered_df = df[
        #     (df["Category"] == category) &
        #     (df["Sanctioned_Load_KW"] == sanctioned_load) &
        #     (df["Consumer No"].astype(str) == str(consumer_no))
        # ]

        filtered_df = df.copy()
        if category is not None:
            filtered_df = filtered_df[filtered_df['Category'] == category]

        if sanctioned_load is not None:
            filtered_df = filtered_df[filtered_df['Sanctioned_Load_KW'] == sanctioned_load]

        if consumer_no is not None:
            filtered_df = filtered_df[filtered_df['Consumer No'].astype(str) == str(consumer_no)]

        # Extract consumption columns
        #consumption_cols = [f"Consumption_Hr_{i}" for i in range(1, 25)]
        consumption_cols = [col for col in filtered_df.columns if col.startswith("Consumption_Hr_")]
        hours = [int(c.split("_")[-1]) for c in consumption_cols]
        if not consumption_cols:
            raise dash.exceptions.PreventUpdate

        if not consumption_cols:
            return go.Figure().update_layout(title="No hourly consumption data found.")
        
        df_consumption = filtered_df[consumption_cols]

        fig = go.Figure()
        for idx, row in df_consumption.iterrows():
            fig.add_trace(go.Scatter(
                x=list(range(1, 25)),
                y=row.values,
                mode="lines",
                name=str(filtered_df.loc[idx, 'Date']) if 'Date' in filtered_df.columns else f"Row {idx}",
                hoverinfo="y"
            ))

        fig.update_layout(
            xaxis=dict(
                tickmode="linear",
                tick0=1,
                dtick=1,
                range=[1, 24],
                title="Hour (1 to 24)"
            ),
            yaxis=dict(title="Consumer Load (kW)"),
            autosize=True,
            legend_title_text="Date",
            height=None
        )
        
        fig.update_traces(line=dict(width=1), opacity=0.4)

        return fig
    
    @app.callback(
        Output("profile-graph", "figure", allow_duplicate=True),
        Input("btn-view-rep-profile", "n_clicks"),
        State("cat-dropdown", "value"),
        State("sanction-dropdown", "value"),
        State("cnumber-dropdown", "value"),
        State("profile-graph", "figure"),
        prevent_initial_call=True
    )
    def overlay_median_profile(n_clicks, category, sanctioned_load, consumer_no, current_fig):

        iso_forest = IsolationForest(contamination=0.5, random_state=42)

        #df = get_scenario_df()

        df = load_cached_df()

        if df is None or not all([category, sanctioned_load, consumer_no]):
            raise dash.exceptions.PreventUpdate

        # filtered_df = df[
        #     (df["Category"] == category) &
        #     (df["Sanctioned_Load_KW"] == sanctioned_load) &
        #     (df["Consumer No"].astype(str) == str(consumer_no))
        # ]

        filtered_df = df.copy()
        if category is not None:
            filtered_df = filtered_df[filtered_df['Category'] == category]

        if sanctioned_load is not None:
            filtered_df = filtered_df[filtered_df['Sanctioned_Load_KW'] == sanctioned_load]

        if consumer_no is not None:
            filtered_df = filtered_df[filtered_df['Consumer No'].astype(str) == str(consumer_no)]

        hr_cols = [col for col in filtered_df.columns if col.startswith("Consumption_Hr_")]
        
        if not hr_cols:
            raise dash.exceptions.PreventUpdate

        # outlier_labels = iso_forest.fit_predict(filtered_df[hr_cols])
        # inliers = filtered_df[outlier_labels == 1]
        # if inliers.empty:
        #     return None
        # inliers_rep_profile = inliers[hr_cols].median()
        #mean_profile.name = consumer_id

        # Compute median profile
        median_profile = filtered_df[hr_cols].median()

        # Extract hour numbers
        hours = [int(c.split("_")[-1]) for c in hr_cols]

        # Load existing figure
        fig = go.Figure(current_fig)

        # Add median profile as a bold red line
        fig.add_trace(go.Scatter(
            x=list(range(1, 25)),
            y=median_profile.values,
            mode="lines",
            name="Representative Profile",
            line=dict(color="black", width=4, dash="dash"),
            marker=dict(size=6),
            hoverinfo="x+y+name"
        ))

        # fig.add_trace(go.Scatter(
        #     x=list(range(1, 25)),
        #     y=inliers_rep_profile.values,
        #     mode="lines",
        #     name="Representative Profile (without outlier)",
        #     line=dict(color="blue", width=4, dash="dash"),
        #     marker=dict(size=6),
        #     hoverinfo="x+y+name"
        # ))

        #fig.update_traces(line=dict(width=0.5), opacity=0.2)

        return fig




    # @app.callback(
    #     Output("profile-graph", "figure", allow_duplicate=True),
    #     Output("logs-area", "children", allow_duplicate=True),
    #     Input("selected-hours-store", "data"),
    #     State("profile-graph", "figure"),
    #     prevent_initial_call=True
    # )
    # def update_tou_lines(selected_hours, current_fig):
    #     if not current_fig:
    #         raise dash.exceptions.PreventUpdate

    #     fig = go.Figure(current_fig)

    #     # Remove old vlines if any (optional: clear shapes)
    #     fig.update_layout(shapes=[])  # Clears existing vlines

    #     if not selected_hours:
    #         return fig, "⚠️ No hours selected."

    #     # Add vertical lines for selected hours
    #     for hr in selected_hours:
    #         fig.add_vline(
    #             x=hr,
    #             line=dict(color="red", dash="dash", width=1),
    #             annotation_text=f"Hr {hr}",
    #             annotation_position="top",
    #             opacity=0.5
    #         )

    #     return fig, ""  

    @app.callback(
        Output("profile-graph", "figure", allow_duplicate=True),
        Output("logs-area", "children", allow_duplicate=True),
        Input("selected-hours-store", "data"),
        State("profile-graph", "figure"),
        prevent_initial_call=True
    )
    def update_tou_bands(selected_hours, current_fig):
        """Add shaded ToU timebands based on selected hours."""
        if not current_fig:
            raise dash.exceptions.PreventUpdate

        fig = go.Figure(current_fig)
        fig.update_layout(shapes=[])  # Clear previous shapes

        if not selected_hours:
            return fig, "⚠️ No ToU hours selected."

        selected_hours = sorted(selected_hours)
        logs = []

        # --- Identify continuous bands ---
        bands = []
        start = prev = selected_hours[0]
        for h in selected_hours[1:]:
            if h != prev + 1:
                bands.append((start, prev))
                start = h
            prev = h
        bands.append((start, prev))  # Add last one

        # --- Assign colors for each band ---
        colors = [
            "rgba(255, 99, 71, 0.2)",   # Tomato
            "rgba(54, 162, 235, 0.2)",  # Blue
            "rgba(255, 206, 86, 0.2)",  # Yellow
            "rgba(75, 192, 192, 0.2)",  # Teal
            "rgba(153, 102, 255, 0.2)", # Purple
            "rgba(255, 159, 64, 0.2)"   # Orange
        ]

        for i, (start_hr, end_hr) in enumerate(bands):
            color = colors[i % len(colors)]
            fig.add_shape(
                type="rect",
                x0=start_hr - 0.5,
                x1=end_hr + 0.5,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                fillcolor=color,
                opacity=0.25,
                layer="below",
                line_width=0,
            )
            logs.append(f"🟩 Highlighted band: {start_hr}–{end_hr}")

        # --- Update layout annotations and legend ---
        fig.update_layout(
            title="Consumer Load Profile with ToU Bands",
            xaxis=dict(title="Time Block", tickangle=90),
            yaxis=dict(title="Load (kW)"),
            shapes=fig.layout.shapes
        )

        if logs:
            msg = "\n".join(logs)
        else:
            msg = "⚠️ No ToU bands drawn."

        return fig, msg

       
    #############################
    ####### STEP 4 ############## SELECT TOU DYNAMICITY
    #############################

    @app.callback(
        Output("tou-selection-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("tou-dynamicity-radio", "value"),
        prevent_initial_call=True
    )
    def store_tou_dynamicity(selection):
        ToUDynamicityCache.set(selection)
        msg = f"✅ ToU dynamicity set to: {selection}"
        return msg, html.Div(msg)
    
    #############################
    ####### STEP 4 ############## SELECT HOUR BINS
    #############################


    @app.callback(
        Output("selected-hours-store", "data"),
        Output("hour-selection-status", "children"),
        Input("hour-selection", "value"),
        prevent_initial_call=True
    )
    def store_selected_hours(selected_hours):
        if not selected_hours:
            return [], "⚠️ No hours selected."
        return selected_hours, f"✅ Selected {len(selected_hours)} hour(s): {sorted(selected_hours)}"
    

    #############################
    ####### STEP 5 ############## CONTINUITY OF FIRST LAST BLOCK SETTINGS
    #############################


    @app.callback(
        Output('continuity-setting', 'data'),
        Input('keep-continuous-bins', 'value')
    )
    def update_continuity_setting(value):
        print(f"Continuity Setting is {value}")
        return {'setting': value}

    #############################
    ####### STEP 6 ############## UPLOAD MODEL PARAMETER FILE
    #############################

    @app.callback(
        Output("store-param-file", "data"),
        Output("model-param-upload-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("upload-model-params", "contents"),
        State("upload-model-params", "filename"),
        #State("logs-area", "children"),
        prevent_initial_call=True,
    )
    def handle_param_upload(contents, filename):
        if not contents:
            raise PreventUpdate

        try:
            # Decode content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Save locally
            os.makedirs("temp_data", exist_ok=True)
            file_path = os.path.join("temp_data", filename)

            with open(file_path, "wb") as f:
                f.write(decoded)

            # Cache path for later use
            model_param_Cache.set(file_path)

            print(f"Model param file is {filename} and save dir is {model_param_Cache.get()}")

            # Store file data in memory (for later inspection or plotting)
            param_data = {
                "filename": filename,
                "path": file_path
            }

            return (
                param_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} saved to {file_path}")
            )

        except Exception as e:
            return (
                no_update,
                html.Div("❌ Upload failed."),
                html.Div(f"❌ Error: {str(e)}")
            )
    

    #############################
    ####### STEP 6 ############## 
    #############################


    #############################
    ####### STEP 7 ############## RUN MODEL
    #############################

    from datetime import datetime

    @app.callback(
        Output("logs-area", "children", allow_duplicate=True),
        #Output("log-interval", "disabled"),
        Input("run-tou-button", "n_clicks"),
        State("store-uploaded-file", "data"),
        State("store-param-file", "data"),
        State("selected-hours-store", "data"),
        State('continuity-setting', 'data'),
        prevent_initial_call=True
    )
    def run_tou_model(n_clicks, input_data, model_param, tou_bins, cont_setting):
        
        print("Running TOU model callback...")
        if not n_clicks:
            return no_update
        
        if not input_data:
             print("⚠️ No output file provided.")
        
        if not model_param:
            print("⚠️ No model parameter settings provided.")

            
        if not tou_bins:
                print("⚠️ Please indicate from continuity settings if you want first and last blocks to be continuous.")
        
        if not cont_setting:
            print("⚠️ Please indicate tou bin cut-offs by selecting hours above.")
        

        # Capture print output
        buffer = io.StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = buffer

        
        output_path = SaveDirCache.get()
        
        #customer_demo = input_data.get("path")
        #customer_demo = inputfileDirCache.get() 
        customer_demo = load_cached_df()

        model_param_path = model_param.get("path")

        output_file_name = OutputFileNameCache.get()

        if not output_file_name:
            print("No output file name provided. Please confirm the file name before running.")
            sys.stdout = sys_stdout_backup
            return "⚠️ Please confirm the output file name before running the model."

        # Create unique timestamped output file name
        now = datetime.now()
        datetime_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        output_file_name_dt = f"output_file_{datetime_string}"
        #output_file_name=  OutputFileNameCache.set(output_file_name)  # Store in cache

        print("inside tou callback and printing stored file name")
        print(output_file_name)
        bins_tou =sorted(tou_bins)
        cont_set = cont_setting.get("setting")

        try:
            # Run model
            pages.new_betrand_VM.run(
                customer_data_file=customer_demo
                ,model_input_file=model_param_path
                ,output_folder=output_path
                ,output_file_name_str = output_file_name_dt
                ,tou_bins= bins_tou
                ,total_time_blocks_modelled = 24
                ,cont_setting = cont_set
                ,output_file_name_by_user = output_file_name
            )
            print(f"✅ Model run complete. Output saved as: {output_file_name}.xlsx")

        except Exception as e:
            print(f"❌ Error while running TOU model: {e}")

        finally:
            sys.stdout = sys_stdout_backup

        logs = buffer.getvalue()
        buffer.close()

        return html.Pre(logs, style={"whiteSpace": "pre-wrap"})



    #############################
    ####### STEP 10 #############
    #############################


    # @app.callback(
    #     Output("trigger-new-tab", "children"),
    #     Input("view-optariff-results", "n_clicks"),
    #     prevent_initial_call=True,
    # )
    # def open_new_tab(n_clicks):
    #     if n_clicks:
    #         # Inject JS to open a new tab
    #         return html.Script('window.open("/load-graphs", "_blank");')
    #     return dash.no_update
    
    #from dash import ctx

    @app.callback(
        Output("trigger-new-tab", "children"),
        Input("view-optariff-results", "n_clicks"),
        Input("compare-optariff-results", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_new_tab(n1, n2):
        triggered_id = ctx.triggered_id
        if triggered_id == "view-optariff-results":
            return html.Script('window.open("/load-graphs", "_blank");')
        elif triggered_id == "compare-optariff-results":
            return html.Script('window.open("/compare-results", "_blank");')
        return dash.no_update


