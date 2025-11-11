from dash import html, dcc, Output, Input, callback, Dash
from steps_module import step_upload_data, step_select_output_folder , step_render_graph , step_select_tou_dynamicity, select_tou_bins, first_last_continuity, step_upload_model_param, step_run_model, step_view_results, view_customer_profile
import dash
import plotly.graph_objs as go
from pages.cache import inputfileDirCache , SaveDirCache , ToUDynamicityCache , RepProfileCache , model_param_Cache ,OutputFileNameCache
import sys
from sklearn.ensemble import IsolationForest
import pages


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
                step_select_tou_dynamicity(),
                #step_select_representative_profile(),
                select_tou_bins(),
                first_last_continuity(),
                step_upload_model_param(),
                step_run_model(),
                step_view_results(),
                dcc.Store(id="store-uploaded-file"),
                dcc.Store(id="selected-hours-store", storage_type="session"),
                dcc.Store(id = "continuity-setting", storage_type="session"),
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
import pandas as pd
import os



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
                html.Div(f"✅ File {filename} saved to {file_path}")
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
    ####### STEP 3 ############## VISUALIZE PLOTS
    #############################

    # @app.callback(
    #     Output("visualization-area", "children"),
    #     Output("logs-area", "children", allow_duplicate=True),
    #     Input("plot-consumption-btn", "n_clicks"),
    #     prevent_initial_call=True,
    # )
    # def plot_consumption_profiles(n_clicks):
    #     try:
    #         file_path = inputfileDirCache.get()
    #         print("Found file from f{file_path} in cache")
    #         if not file_path or not os.path.exists(file_path):
    #             raise FileNotFoundError("Uploaded file not found.")

    #         if file_path.endswith(".csv"):
    #             df = pd.read_csv(file_path)
    #             print("Read csv file")
    #         elif file_path.endswith(".xls") or file_path.endswith(".xlsx"):
    #             df = pd.read_excel(file_path)
    #             print("Read excel file")
    #         else:
    #             raise ValueError("Unsupported file type")

    #         # Extract consumption columns
    #         consumption_cols = [f"Consumption_Hr_{i}" for i in range(1, 25)]
    #         df_consumption = df[consumption_cols]

    #         # Create line traces for each row
    #         fig = go.Figure()
    #         for idx, row in df_consumption.iterrows():
    #             fig.add_trace(go.Scatter(
    #                 y=row.values,
    #                 mode="lines",
    #                 #name=f"Consumer {idx+1}",
    #                 line=dict(width=1),
    #                 hoverinfo="y"
    #             ))

    #         fig.update_layout(
    #             title="All Consumption Profiles",
    #             xaxis_title="Hour (1 to 24)",
    #             yaxis_title="Consumer Load (kW)",
    #             template="plotly_white",
    #             showlegend=False,
    #             height=500
    #         )

    #         log_msg = f"✅ Rendered consumption profiles from file: {os.path.basename(file_path)}"
    #         return dcc.Graph(figure=fig, style={"height": "500px"}), html.Div("✅ Rendered plot")

    #     except Exception as e:
    #         err_msg = f"❌ Error rendering plot: {str(e)}"
    #         return go.Figure(), html.Div(err_msg)


    @app.callback(
        Output("cat-dropdown", "options",allow_duplicate=True),
        Output("sanction-dropdown", "options",allow_duplicate=True),
        Output("cnumber-dropdown", "options",allow_duplicate=True),
        Output("logs-area", "children", allow_duplicate=True),
        Input("store-uploaded-file", "data"),
        prevent_initial_call=True
    )
    def populate_dropdowns(uploaded_file):
        try:
            # Get cached file path
            print("Testing....")
            fp = inputfileDirCache.get()  # full path to the uploaded file

            if not fp or not os.path.exists(fp):
                return [], [], [], html.Div("❌ File path is invalid or missing.")

            # Read Excel file
            df = pd.read_excel(fp, parse_dates=["Date"])
            df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')

            # Build dropdown options
            cat_options = [{"label": cat, "value": cat} for cat in sorted(df["Category"].dropna().unique())]
            sanction_options = [{"label": val, "value": val} for val in sorted(df["Sanctioned_Load_KW"].dropna().unique())]
            consumer_options = [{"label": str(cn), "value": str(cn)} for cn in sorted(df["Consumer No"].dropna().unique())]

            return cat_options, sanction_options, consumer_options, html.Div("✅ Dropdowns populated.")
        
        except Exception as e:
            return [], [], [], html.Div(f"❌ Dropdown error: {str(e)}")
        
    @app.callback(
        Output("profile-graph", "figure",allow_duplicate=True),
        Input("cat-dropdown", "value"),
        Input("sanction-dropdown", "value"),
        Input("cnumber-dropdown", "value"),
        prevent_initial_call=True
    )


    def update_graph(category, sanctioned_load, consumer_no):
        df = get_scenario_df()

        # Ensure data exists and all filters are provided
        if df is None or not all([category, sanctioned_load, consumer_no]):
            raise dash.exceptions.PreventUpdate

        # Filter data
        filtered_df = df[
            (df["Category"] == category) &
            (df["Sanctioned_Load_KW"] == sanctioned_load) &
            (df["Consumer No"].astype(str) == str(consumer_no))
        ]

        #-----------------
        # Extract hourly columns
        # hr_cols = [col for col in filtered_df.columns if col.startswith("Consumption_Hr_")]
        # # print(hr_cols)
        # # if not hr_cols:
        # #     return go.Figure().update_layout(title="No hourly consumption data found.")

        # # # Melt dataframe to long format for plotting
        # # melted_df = filtered_df.melt(
        # #     id_vars=["Date_str"],
        # #     value_vars=hr_cols,
        # #     var_name="Hour",
        # #     value_name="Consumption"
        # # )


        # # # Extract hour numbers (1–24) from column names
        # # melted_df["Hour"] = melted_df["Hour"].str.extract(r"(\d+)").astype(int)

        # # print(melted_df)
        # # # Create line plot using Plotly Express
        # # fig = px.line(
        # #     melted_df,
        # #     x="Hour",
        # #     y="Consumption",
        # #     color="Date_str",
        # #     title="Hourly Consumption for Selected Consumer",
        # #     labels={"Date_str": "Date"},
        # # )

        # fig.update_layout(
        #     autosize=True,
        #     height=None,
        #     xaxis_title="Hour (1 to 24)",
        #     yaxis_title="Consumer Load (kW)",
        #     template="plotly_white",
        #     legend_title_text="Date"
        # )

        #-----------------

        # Extract consumption columns
        consumption_cols = [f"Consumption_Hr_{i}" for i in range(1, 25)]

        if not consumption_cols:
            return go.Figure().update_layout(title="No hourly consumption data found.")
        
        df_consumption = filtered_df[consumption_cols]

        # Create line traces for each row
        fig = go.Figure()
        for idx, row in df_consumption.iterrows():
            fig.add_trace(go.Scatter(
                x=list(range(1, 25)),
                y=row.values,
                mode="lines",
                name=f"{filtered_df[idx,'Date']}",
                line=dict(width=0.5),
                hoverinfo="y"
            ))

        fig.update_layout(
            xaxis=dict(
                x=list(range(1, 25)),
                tickmode="linear",
                tick0=1,
                dtick=1,
                range=[1, 25]  # Force display of hours 1 to 24
            ),
            autosize=True,
            height=None,
            xaxis_title="Hour (1 to 24)",
            yaxis_title="Consumer Load (kW)",
            template="plotly_white",
            legend_title_text="Date"
        )
        
        fig.update_traces(line=dict(width=0.5), opacity=0.2)

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

        df = get_scenario_df()
        if df is None or not all([category, sanctioned_load, consumer_no]):
            raise dash.exceptions.PreventUpdate

        filtered_df = df[
            (df["Category"] == category) &
            (df["Sanctioned_Load_KW"] == sanctioned_load) &
            (df["Consumer No"].astype(str) == str(consumer_no))
        ]

        hr_cols = [col for col in filtered_df.columns if col.startswith("Consumption_Hr_")]
        if not hr_cols:
            raise dash.exceptions.PreventUpdate

        outlier_labels = iso_forest.fit_predict(filtered_df[hr_cols])
        inliers = filtered_df[outlier_labels == 1]
        if inliers.empty:
            return None
        inliers_rep_profile = inliers[hr_cols].median()
        #mean_profile.name = consumer_id

        # Compute median profile
        median_profile = filtered_df[hr_cols].median()

        # Extract hour numbers
        hours = [int(c.split("_")[-1]) for c in hr_cols]

        # Load existing figure
        fig = go.Figure(current_fig)

        # Add median profile as a bold red line
        fig.add_trace(go.Scatter(
            x=hours,
            y=median_profile.values,
            mode="lines",
            name="Representative Profile",
            line=dict(color="black", width=4, dash="dash"),
            marker=dict(size=6),
            hoverinfo="x+y+name"
        ))

        fig.add_trace(go.Scatter(
            x=hours,
            y=inliers_rep_profile.values,
            mode="lines",
            name="Representative Profile (without outlier)",
            line=dict(color="blue", width=4, dash="dash"),
            marker=dict(size=6),
            hoverinfo="x+y+name"
        ))

        return fig

    # @app.callback(
    #     Output("profile-graph", "figure", allow_duplicate=True),
    #     Output("logs-area", "children"),
    #     Input("btn-view-tou-bins", "n_clicks"),
    #     State("selected-hours-store", "data"),
    #     State("profile-graph", "figure"),
    #     prevent_initial_call=True
    # )
    # def add_tou_bins(n_clicks, selected_hours, current_fig):
    #     if not selected_hours:
    #         return dash.no_update, "⚠️ No hours selected."

    #     fig = go.Figure(current_fig)  # Use current figure

    #     # Add vertical lines for selected hours
    #     for hr in selected_hours:
    #         fig.add_vline(
    #             x=hr,
    #             line=dict(color="black", dash="dash", width=1),
    #             annotation_text=f"Hr {hr}",
    #             annotation_position="top",
    #             opacity=0.5
    #         )

    #     return fig, ""   

    @app.callback(
        Output("profile-graph", "figure", allow_duplicate=True),
        Output("logs-area", "children"),
        Input("selected-hours-store", "data"),
        State("profile-graph", "figure"),
        prevent_initial_call=True
    )
    def update_tou_lines(selected_hours, current_fig):
        if not current_fig:
            raise dash.exceptions.PreventUpdate

        fig = go.Figure(current_fig)

        # Remove old vlines if any (optional: clear shapes)
        fig.update_layout(shapes=[])  # Clears existing vlines

        if not selected_hours:
            return fig, "⚠️ No hours selected."

        # Add vertical lines for selected hours
        for hr in selected_hours:
            fig.add_vline(
                x=hr,
                line=dict(color="red", dash="dash", width=1),
                annotation_text=f"Hr {hr}",
                annotation_position="top",
                opacity=0.5
            )

        return fig, ""  
       
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
    ####### STEP 5 ##############
    #############################

    # @app.callback(
    #     Output("visualization-area", "children"),
    #     Output("logs-area", "children", allow_duplicate = True),
    #     Input("visualise-median-profile-button", "n_clicks"),
    #     State("stored-input-file-path", "data"),
    #     State("stored-output-folder-path", "data"),
    #     prevent_initial_call=True
    # )
    # def generate_representative_profile(n_clicks, input_path, output_dir):
    #     if n_clicks == 0:
    #         raise dash.exceptions.PreventUpdate

    #     try:
    #         if not input_path or not output_dir:
    #             return dash.no_update, "Missing input file or output directory."

    #         if input_path.endswith(".csv"):
    #             df = pd.read_csv(input_path)
    #         elif input_path.endswith(".xls") or input_path.endswith(".xlsx"):
    #             df = pd.read_excel(input_path)
    #         else:
    #             return dash.no_update, "Unsupported file format"

    #         consumption_cols = [col for col in df.columns if col.startswith("Consumption_Hr_")]
    #         if df.empty or not consumption_cols:
    #             return dash.no_update, "Empty or invalid file"

    #         fig = go.Figure()
    #         for _, row in df.iterrows():
    #             fig.add_trace(go.Scatter(
    #                 x=list(range(1, len(consumption_cols) + 1)),
    #                 y=row[consumption_cols],
    #                 mode='lines',
    #                 line=dict(color='lightgray'),
    #                 hoverinfo="y",
    #                 showlegend=False
    #             ))

    #         median_profile = df[consumption_cols].median()
    #         fig.add_trace(go.Scatter(
    #             x=list(range(1, len(consumption_cols) + 1)),
    #             y=median_profile,
    #             mode='lines+markers',
    #             name='Median Profile',
    #             line=dict(color='blue', width=3)
    #         ))

    #         fig.update_layout(
    #             title="All Consumption Profiles with Median",
    #             xaxis_title="Hour",
    #             yaxis_title="Consumption (kW)",
    #             template="plotly_white",
    #             height=500
    #         )

    #         # Save CSV
    #         median_df = pd.DataFrame([median_profile])
    #         output_path = os.path.join(output_dir, "representative_profile.csv")
    #         median_df.to_csv(output_path, index=False)

    #         return fig, f"Representative profile saved to: {output_path}"
        
    #     except Exception as e:
    #         return dash.no_update, f"Error: {str(e)}"


    #############################
    ####### STEP 6 ##############
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
    ####### STEP 7 ##############
    #############################


    #############################
    ####### STEP 8 ##############
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
    ####### STEP 9 ##############
    #############################

    # @app.callback(
    #     Output("logs-area", "children", allow_duplicate=True),
    #     Input("run-tou-button", "n_clicks"),
    #     State("store-uploaded-file", "data"),
    #     State("store-param-file", "data"),
    #     prevent_initial_call=True
    # )
    # def run_tou_model(n_clicks, input_data, model_param):
    #     print("Running TOU model callback...")
    #     if not n_clicks or not input_data or not model_param:
    #         return no_update

    #     # Capture print output
    #     buffer = io.StringIO()
    #     sys_stdout_backup = sys.stdout
    #     sys.stdout = buffer

    #     output_path = SaveDirCache.get()
    #     customer_demo = input_data.get("path")
    #     model_param_path = model_param.get("path")

    #     try:
    #         pages.new_betrand_VM.run(customer_data_file=customer_demo,
    #                                 model_input_file=model_param_path,
    #                                 output_folder=output_path)

    #     except Exception as e:
    #         print(f"Error while running TOU model: {e}")

    #     finally:
    #         sys.stdout = sys_stdout_backup

    #     logs = buffer.getvalue()
    #     buffer.close()

    #     return html.Pre(logs, style={"whiteSpace": "pre-wrap"})

    @app.callback(
        Output('continuity-setting', 'data'),
        Input('keep-continuous-bins', 'value')
    )
    def update_continuity_setting(value):
        print(f"Continuity Setting is {value}")
        return {'setting': value}

    from datetime import datetime

    @app.callback(
        Output("logs-area", "children", allow_duplicate=True),
        Input("run-tou-button", "n_clicks"),
        State("store-uploaded-file", "data"),
        State("store-param-file", "data"),
        State("selected-hours-store", "data"),
        State('continuity_setting', 'data'),
        prevent_initial_call=True
    )
    def run_tou_model(n_clicks, input_data, model_param, tou_bins, cont_setting):
        print("Running TOU model callback...")
        if not n_clicks or not input_data or not model_param or not cont_setting:
            return no_update

        # Capture print output
        buffer = io.StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = buffer

        output_path = SaveDirCache.get()
        customer_demo = input_data.get("path")
        model_param_path = model_param.get("path")

        # Create unique timestamped output file name
        now = datetime.now()
        datetime_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        output_file_name = f"output_file_{datetime_string}"
        OutputFileNameCache.set(output_file_name)  # Store in cache

        bins_tou =sorted(tou_bins)
        cont_set = cont_setting.get("setting")
        try:
            # Run model
            pages.new_betrand_VM.run(
                customer_data_file=customer_demo,
                model_input_file=model_param_path,
                output_folder=output_path,
                output_file_name_str = output_file_name, tou_bins= bins_tou, cont_setting = cont_set
            )
            print(f"✅ Model run complete. Output saved as: {output_file_name}")

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

    @app.callback(
        Output("redirect1", "href"),
        Input("view-optariff-results", "n_clicks"),
        prevent_initial_call=True,
    )
    def redirect_on_click(n_clicks):
        if n_clicks:
            return "/load-graphs"
        return dash.no_update
    

#     # ✅ Register your callbacks here
# def register_callbacks(app):
#     @app.callback(
#         Output("redirect", "href"),
#         Input("btn-individual", "n_clicks"),
#         Input("btn-cluster", "n_clicks"),
#         prevent_initial_call=True
#     )
#     def redirect_on_click(n1, n2):
#         triggered_id = ctx.triggered_id
#         if triggered_id == "btn-individual":
#             return "/run-individual-model"
#         elif triggered_id == "btn-cluster":
#             return "/run-cluster-model"
#         return dash.no_update
    