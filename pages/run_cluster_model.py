from dash import html, dcc, Output, Input, callback, Dash
from steps_module_cluster import step_upload_data, step_select_output_folder , view_cluster_tabs , step_select_tou_dynamicity, select_tou_bins, first_last_continuity, step_upload_model_param, step_run_model, step_view_results
import dash
import plotly.graph_objs as go
from pages.cache import inputfileDirCache , SaveDirCache , ToUDynamicityCache , RepProfileCache , model_param_Cache , OutputFileNameCache, ClusterfileDirCache, ConsumptionValuesCache
import sys
from sklearn.ensemble import IsolationForest
import pages
from pages import make_monthly_cons
from pages.plot_clusters import get_cluster_plot_figure
from pages import clustering
from dash.exceptions import PreventUpdate
#from pages import new_betrand_cluster_model
from dash import html, dcc, ctx
from pages.run_individual_model import extract_and_cache_consumers
from pages.cache import ConsumerListCache, TimeBlockRangeCache, TouBinsCache
import re
from config import CONSUMER_PATTERNS, CATEGORY_PATTERNS, CONNECTED_LOAD_PATTERNS, TIMEBLOCK_PATTERNS

## Logic is as follows:
# 1. User uploads data. if he isn't sure of format, he can download and see required format
# 2. User can now start visualizing from first tab, he can now explore the attribute distribution to help guide clustering
# 3. User can then select clustering options
# 4. Then, remaining is as per run individual model


time_block_patterns = TIMEBLOCK_PATTERNS['TIMEBLOCK_PATTERNS']

def _timeblock_columns(columns, TIMEBLOCK_PATTERNS):
    """Identify time block columns using patterns from config."""
    regex_patterns = TIMEBLOCK_PATTERNS["regex"]
    prefix_patterns = TIMEBLOCK_PATTERNS["prefix"]

    # Try regex matches first
    combined_regex = "|".join(f"({p})" for p in regex_patterns)
    patt = re.compile(combined_regex, re.IGNORECASE)
    cols = [c for c in columns if patt.fullmatch(c)]

    if not cols:
        # fallback to prefix matching
        cols = [
            c for c in columns
            if any(c.lower().startswith(prefix) for prefix in prefix_patterns)
        ]

    return cols




def cache_timeblock_range(columns, time_block_patterns):
    """
    Identify time-block/hour columns and cache the first and last numeric indices.
    Works for patterns like ImportkWhTimeBlock1...48 or Consumption_Hr_1...24
    """
    import re

    tb_cols = _timeblock_columns(columns, TIMEBLOCK_PATTERNS= time_block_patterns)
    if not tb_cols:
        print("[WARN] No timeblock columns detected.")
        return

    # Extract numeric parts from column names
    nums = []
    for c in tb_cols:
        match = re.search(r'(\d+)', c)
        if match:
            nums.append(int(match.group(1)))

    if nums:
        first = min(nums)
        last = max(nums)
        TimeBlockRangeCache.set(first, last)
    else:
        print("[WARN] No numeric suffix found in timeblock columns.")



# Layout
layout = html.Div(
    style={"display": "flex", "height": "100vh", "fontFamily": "Inter, sans-serif"},
    children=[
        dcc.Store(id="store-uploaded-file1", storage_type="session"),
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
                dcc.Store(id="store-uploaded-file1"),
                dcc.Store(id="selected-hours-store1", storage_type="session"),
                dcc.Store(id = "continuity-setting1", storage_type="session"),
                dcc.Store(id = "store-final-clustered-data", data =  {"clustered_data": "", "medoid_data": ""}, storage_type="session"),
            ]
        ),

        # Right Panel – Divided into 3 sections: logo, graph area, logs
        html.Div(
            style={"flex": "3", "display": "flex", "flexDirection": "column", "padding": "20px"},
            children=[

                # Top: Logo
                html.Div(
                    id="1logo-area",
                    style={
                        "height": "80px",
                        "marginBottom": "10px",
                        "display": "flex",
                        "justifyContent": "flex-end",
                        "alignItems": "center"
                    },
                    children=[
                        html.Img(src="/assets/CEA logo.png", style={"height": "60px"})
                    ]
                ),

                # Middle: Interactive visualization area
                html.Div(
                    id="1visualization-area",
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
                        view_cluster_tabs()

                    ]
                ),

                # Bottom: Logs area
                html.Div(
                    id="logs-area1",
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
            parse_dates=["Date"],
            engine='openpyxl'
        )
        df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
        return df

    return None


def register_callbacks(app):

    #############################
    ####### STEP 1 ############## READ INPUT FILE
    ############################# 

    # @app.callback(
    #     Output("store-uploaded-file1", "data"),
    #     Output("file-upload-status1", "children"),
    #     Output("logs-area1", "children", allow_duplicate=True),
    #     Input("upload-data1", "contents"),
    #     State("upload-data1", "filename"),
    #     #State("logs-area1", "children"),
    #     prevent_initial_call=True,
    # )
    # def handle_file_upload(contents, filename):
    #     if not contents:
    #         raise PreventUpdate
    #
    #     try:
    #         # Decode content
    #         content_type, content_string = contents.split(',')
    #         decoded = base64.b64decode(content_string)
    #
    #         # Save locally
    #         os.makedirs("temp_data", exist_ok=True)
    #         file_path = os.path.join("temp_data", filename)
    #
    #         with open(file_path, "wb") as f:
    #             f.write(decoded)
    #
    #         # Cache path for later use
    #         inputfileDirCache.set(file_path)
    #
    #         # Store file data in memory (for later inspection or plotting)
    #         store_data = {
    #             "filename": filename,
    #             "path": file_path
    #         }
    #
    #         return (
    #             store_data,
    #             html.Div(f"✅ Uploaded file: {filename}."),
    #             html.Div(f"✅ File {filename} is ready to visualize. ‼️ Please select Ouput Directory before visualizing and then Select options in *Investigate Distribution* and  *Clustering Tool tabs* on the right-hand-side panel.")
    #         )
    #
    #     except Exception as e:
    #         return (
    #             no_update,
    #             html.Div("❌ Upload failed."),
    #             html.Div(f"❌ Error: {str(e)}")
    #         )

    @app.callback(
        Output("data-input-area1", "children"),
        Input("data-source-type1", "value"),
    )
    def toggle_data_input(source_type):
        """Dynamically display the correct UI based on data source selection."""
        common_style = {
            "width": "100%",
            "height": "70px",
            "lineHeight": "70px",
            "borderWidth": "2px",
            "borderStyle": "dashed",
            "borderRadius": "12px",
            "textAlign": "center",
            "backgroundColor": "#f9f9f9",
            "color": "#555",
            "fontSize": "14px",
            "fontWeight": "500",
            "cursor": "pointer",
            "marginBottom": "10px",
        }

        # if source_type == "file":
        #     return html.Div([
        #         dcc.Upload(
        #             id="upload-data",
        #             children=html.Div("📂 Drag & drop or click to upload CSV/Excel file"),
        #             style=common_style,
        #             multiple=False
        #         ),
        #         html.Div(id="file-upload-status", style={
        #             "fontSize": "13px",
        #             "color": "#134A94",
        #             "marginTop": "8px"
        #         }),
        #     ])
        if source_type == "file":
            return html.Div([
                html.Div(
                    "📄 Click to select CSV/Excel file",
                    id="select-file-path-btn1",
                    n_clicks=0,
                    style=common_style
                ),
                html.Div(id="file-upload-status1", style={
                    "fontSize": "13px",
                    "color": "#134A94",
                    "marginTop": "8px"
                }),
            ])

        elif source_type == "duckdb":
            return html.Div([
                html.Div(
                    "🦆 Click to select DuckDB file",
                    id="select-duckdb-path-btn1",
                    n_clicks=0,
                    style=common_style
                ),
                html.Div(id="duckdb-path-status1", style={
                    "fontSize": "13px",
                    "color": "#134A94",
                    "marginTop": "8px"
                }),
            ])

        return html.Div("Please select a data source type above.")

    """ DUCK AND CSV SELECTION """

    @app.callback(
        Output("file-upload-status1", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("select-file-path-btn1", "n_clicks"),
        prevent_initial_call=True,
    )
    def select_local_csv_excel(n_clicks):
        """Let the user pick a CSV/Excel file from disk and cache its path."""
        if not n_clicks:
            raise PreventUpdate

        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askopenfilename(
                title="Select CSV/Excel file",
                filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")],
            )
            root.destroy()

            if not file_path:
                msg = "❌ No file selected or dialog cancelled."
                return html.Div(msg, style={"color": "red"}), html.Div(msg)

            # cache the path for later readers
            inputfileDirCache.set(file_path)
            extract_and_cache_consumers(file_path)
            print(f"[CACHE] File selected: {file_path}")
            print(f"[VERIFY CSV/EXCEL] Cache now holds: {inputfileDirCache.get()}")


            """ Dynamically Save the Time Block """


            # ✅ Try reading a small preview to verify and inspect columns
            try:
                # import pandas as pd

                if file_path.lower().endswith(".csv"):
                    df_preview = pd.read_csv(file_path)
                    print(f"[INFO] CSV file loaded successfully. Columns: {list(df_preview.columns)}")

                    cache_timeblock_range(columns = df_preview.columns, time_block_patterns= time_block_patterns)


                elif file_path.lower().endswith((".xlsx", ".xls")):
                    df_preview = pd.read_excel(file_path)
                    print(f"[INFO] Excel file loaded successfully. Columns: {list(df_preview.columns)}")

                    cache_timeblock_range(columns=df_preview.columns, time_block_patterns = time_block_patterns)
                    print(TimeBlockRangeCache.get())

                else:
                    print("[WARN] Unsupported file format for preview.")

            except Exception as e:
                print(f"[ERROR] Failed to read preview: {e}")

            msg = f"✅ Selected file: {file_path}"
            return html.Div(msg, style={"color": "#134A94"}), html.Div(f"✅ File path saved: {file_path}")

        except Exception as e:
            err = f"❌ Error selecting file: {e}"
            return html.Div(err, style={"color": "red"}), html.Div(err)

    @app.callback(
        Output("duckdb-path-status1", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("select-duckdb-path-btn1", "n_clicks"),
        prevent_initial_call=True,
    )
    def select_duckdb_file(n_clicks):
        """Open DuckDB file picker safely from a background thread."""
        result_queue = queue.Queue()

        # -------------------------------
        # Ask user for file path
        # -------------------------------
        def open_dialog(q):
            import tkinter as tk
            from tkinter import filedialog
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                duck_path = filedialog.askopenfilename(
                    title="Select DuckDB File",
                    filetypes=[("DuckDB files", "*.duckdb")],
                )
                q.put(duck_path if duck_path else None)
            except Exception as e:
                q.put(f"Error: {e}")
            finally:
                try:
                    root.destroy()
                except:
                    pass

        t = threading.Thread(target=open_dialog, args=(result_queue,), daemon=True)
        t.start()
        t.join()

        duck_path = result_queue.get() if not result_queue.empty() else None

        # -----------------------------------
        # No file selected → immediate return
        # -----------------------------------
        if not duck_path or isinstance(duck_path, str) and duck_path.startswith("Error:"):
            msg = "❌ No file selected."
            return html.Div(msg, style={"color": "red"}), html.Div(msg)

        # -----------------------------------------------
        # IMMEDIATE return to update UI / logs instantly
        # -----------------------------------------------
        immediate_log = f"📁 File selected: {duck_path}. Processing..."
        status_msg = f"✅ Selected DuckDB file: {duck_path}"

        # Return immediately so logs update
        # -----------------------------------------------
        # **Fire background processing thread**
        # -----------------------------------------------
        def background_work(path):
            try:
                print("[THREAD] Background processing started...")

                # Store path
                inputfileDirCache.set(path)

                # Extract consumers
                extract_and_cache_consumers(path)

                # Verify DuckDB
                import duckdb
                con = duckdb.connect(path, read_only=True)
                tables = con.execute("SHOW TABLES").fetchall()
                if tables:
                    table_name = tables[0][0]
                    df_preview = con.execute(
                        f"SELECT * FROM {table_name} LIMIT 5"
                    ).fetchdf()

                    cache_timeblock_range(
                        df_preview.columns,
                        time_block_patterns=time_block_patterns
                    )

                con.close()

                # LOG SUCCESS
                final_msg = f"✅ DuckDB verified and cached successfully: {path}"
                print("[LOG]", final_msg)

            except Exception as e:
                final_msg = f"❌ DuckDB processing failed: {e}"
                print("[LOG]", final_msg)

        threading.Thread(
            target=background_work,
            args=(duck_path,),
            daemon=True
        ).start()

        # UI gets updated immediately (without waiting)
        return (
            html.Div(status_msg, style={"color": "#134A94"}),
            html.Div(immediate_log),
        )

    #############################
    ####### STEP 2 ############## SELECT OUTPUT DIRECTORY
    #############################    

    @app.callback(
        Output("selected-folder-path1", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Output("output-folder-store1", "data"),
        Input("select-output-folder-btn1", "n_clicks"),
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

            msg = f"✅ Output folder set to: {abs_path}."

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


    @app.callback(
        Output("output-file-name-store1", "data"),
        Output("output-file-name-log1", "children"),
        Input("confirm-output-filename-btn1", "n_clicks"),
        State("output-file-name-input1", "value"),
        prevent_initial_call=True
    )
    
    def store_output_file_name(n_clicks, file_name):
        if file_name:
            cleaned_name = file_name.strip()
            #print("file_name_testing_ok")
            if not cleaned_name or cleaned_name.lower() in ['output', 'con', 'nul']:  # Windows reserved words
                return no_update, "⚠️ Please enter a valid output file name."
            #print("file_cache_testing_ok")
            OutputFileNameCache.set(cleaned_name)
            return cleaned_name, f"✅ Output file name saved as: {cleaned_name}.xlsx"

        OutputFileNameCache.set(None)
        return "", "⚠️ Please enter a valid output file name."
    
    #############################
    ####### STEP 3 ############## VISUALIZE PLOTS in TAB 1
    #############################


    @app.callback(
        Output("distribution-plot1", "figure"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("distribution-attribute-dropdown1", "value"),
        Input("store-uploaded-file1", "data"),
        prevent_initial_call=True
    )
    def update_distribution_plot(selected_attribute, uploaded_data):
        logs = []

        try:
            fp = inputfileDirCache.get()  # full path to the uploaded file
            logs.append(f"📂 Reading file path: {fp}")

            if not fp or not os.path.exists(fp):
                logs.append("❌ File path is invalid or missing.")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            # Read the file based on extension
            if fp.endswith(".csv"):
                df = pd.read_csv(fp)
                logs.append("✅ Loaded CSV file.")
            elif fp.endswith(".xls") or fp.endswith(".xlsx"):
                df = pd.read_excel(fp, engine='openpyxl')
                logs.append("✅ Loaded Excel file.")

            elif fp.endswith(".duckdb") or fp.endswith(".db"):
                import duckdb
                logs.append("🦆 Detected DuckDB database file.")
                try:
                    # Connect to DuckDB and read all tables or a specific one
                    con = duckdb.connect(database=fp, read_only=True)

                    # List all tables in the DuckDB file
                    tables = con.execute("SHOW TABLES").fetchall()
                    logs.append(f"📋 Tables found: {[t[0] for t in tables]}")

                    if tables:
                        # Read the first table by default (you can modify this)
                        table_name = tables[0][0]
                        df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
                        logs.append(f"✅ Loaded table '{table_name}' from DuckDB file.")
                        print(df.columns)
                    else:
                        logs.append("❌ No tables found in DuckDB file.")
                        df = pd.DataFrame()

                except Exception as e:
                    logs.append(f"❌ Error reading DuckDB file: {e}")
                    df = pd.DataFrame()

                finally:
                    con.close()

            else:
                logs.append("❌ Unsupported file format.")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'],  format="%d-%m-%Y", errors='coerce')
                df['Date_str'] = df['Date'].dt.strftime('%d-%m-%Y')
                logs.append("📅 Converted 'Date' column to datetime.")
            else:
                logs.append("⚠️ 'Date' column not found. Skipping date conversion.")

            # Input validation
            if not selected_attribute:
                logs.append("⚠️ No attribute selected.")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            print(f" SELECTED ATTRIBUTE is {selected_attribute}")
            # if selected_attribute not in df.columns and selected_attribute not in ['Sanctioned_Load_KW', 'monthly_consumption']:
            #     logs.append(f"❌ Selected attribute '{selected_attribute}' not found in data.")
            #     return go.Figure(), html.Ul([html.Li(log) for log in logs])

            df_columns = [str(c).strip() for c in df.columns]
            matched_cons_num = [c for c in df_columns if any(p in c.lower() for p in CONSUMER_PATTERNS)]

            if 'Consumer No' in df.columns:
                cons_col = 'Consumer No'

            else:
                cons_col = matched_cons_num[0]

            group_col,x_label = None, None

            # Handle binning logic
            if selected_attribute == 'Sanctioned_Load_KW':


                if selected_attribute in df.columns:
                    if 'sanctioned_load_bin' not in df.columns:
                        #bins = [0, 1, 2, 3, 5, 10, 20, 50, 100, float('inf')]
                        #labels = ['0-1', '1-2', '2-3', '3-5', '5-10', '10-20', '20-50', '50-100', '100+']

                        df['sanctioned_load_bin'] = pd.qcut(df['Sanctioned_Load_KW'], q=10, duplicates='drop')

                        #df['sanctioned_load_bin'] = pd.cut(df['Sanctioned_Load_KW'], bins=bins, labels=labels, right=False)
                        logs.append("📊 Created sanctioned load bins.")

                else:

                    matched_cols = [c for c in df_columns if any(p in c.lower() for p in CONNECTED_LOAD_PATTERNS)]

                    if 'sanctioned_load_bin' not in df.columns:
                        #bins = [0, 1, 2, 3, 5, 10, 20, 50, 100, float('inf')]
                        #labels = ['0-1', '1-2', '2-3', '3-5', '5-10', '10-20', '20-50', '50-100', '100+']

                        df['sanctioned_load_bin'] = pd.qcut(df[matched_cols[0]], q=10, duplicates='drop')

                        #df['sanctioned_load_bin'] = pd.cut(df['Sanctioned_Load_KW'], bins=bins, labels=labels, right=False)
                        logs.append(f"📊 Created sanctioned load bins from column --- {matched_cols[0]}")


                group_col = 'sanctioned_load_bin'
                x_label = 'Sanctioned Load Bin (kW)'

            elif selected_attribute == 'monthly_consumption':
                consumption_cols = _timeblock_columns(columns = df.columns, TIMEBLOCK_PATTERNS = time_block_patterns)

                ConsumptionValuesCache.set(consumption_cols)

                print(consumption_cols)
                #consumption_cols = [col for col in df.columns if col.startswith('Consumption_Hr_')]
                #df['Year'] = df['Date'].dt.year
                df['Month'] = df['Date'].dt.month.astype(str)
                df['Year'] = df['Date'].dt.year.astype(str)      
                
                print(min(df['Month']))
                print(min(df['Year']))
                print(max(df['Month']))
                print(max(df['Year']))

                #df['total_consumption'] = df[consumption_cols].sum(axis=1)
                df['daily_demand'] = df[consumption_cols].sum(axis=1).round(0)    

                print("checking consumption logic")
                print(min(df['daily_demand']))
                print(max(df['daily_demand']))
                # Now group by Consumer No, Year and Month, then sum total_consumption to get monthly consumption
                #monthly_consumption_df = df.groupby(['Consumer No', 'Month', 'Year'])['daily_demand'].sum().reset_index()

                monthly_consumption_df = df.groupby([cons_col, 'Month', 'Year'])['daily_demand'].sum().reset_index(name='total_monthly_consumption')
                monthly_consumption_df['Month'] = monthly_consumption_df['Month'].astype(str)
                monthly_consumption_df['Month'] = monthly_consumption_df['Month'].astype(str)
                monthly_consumption_df['total_monthly_consumption'] = monthly_consumption_df['total_monthly_consumption'].round(0)

                print(monthly_consumption_df.columns)
                # Rename for clarity
                #monthly_consumption_df.rename(columns={'daily_demand': 'monthly_consumption'}, inplace=True)
                print("testing after grouping")
                print(max(monthly_consumption_df['total_monthly_consumption']))  

                print(monthly_consumption_df.columns)
                if 'total_monthly_consumption' not in df.columns:
                    df = df.merge(monthly_consumption_df[[cons_col, 'Year', 'Month', 'total_monthly_consumption']], on=[cons_col, 'Year', 'Month'], how='left')

                print(df.columns)
                print('Minimum consumption ')
                print(min(df['total_monthly_consumption']))
                print(max(df['total_monthly_consumption']))
                
                df.drop(columns=['Year', 'Month'], inplace=True)
                print(df.columns)
                if 'monthly_consumption_bin' not in df.columns:

                    df['monthly_consumption_bin'] = pd.qcut(df['total_monthly_consumption'], q=10, duplicates='drop')
                    logs.append("📊 Created monthly consumption bins.")

                group_col = 'monthly_consumption_bin'
                x_label = 'Monthly Consumption Bin'

            elif selected_attribute == 'Category':

                if selected_attribute in df.columns:
                    group_col = selected_attribute
                    x_label = selected_attribute

                else:

                    matched_category = [c for c in df_columns if any(p in c.lower() for p in CATEGORY_PATTERNS)]
                    if len(matched_category) > 0:
                        group_col = matched_category[0]
                        x_label = matched_category[0]

                        print(f"CATEGORY --- {group_col}")
                    else:

                        print("NO CATEGORY FOUND")


            # Frequency stats
            if cons_col is None:
                logs.append("❌ 'Consumer No' column missing from file.")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            if group_col is None and x_label is None:
                logs.append("❌ Select Attribute Please")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            bin_counts = df.groupby(group_col)[cons_col].nunique().sort_index()
            total_unique = df[cons_col].nunique()
            bin_percent = (bin_counts / total_unique * 100).round(2)

            logs.append(f"✅ Calculated frequency for {group_col}. Total unique consumers: {total_unique}")

            # Create bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=bin_counts.index.astype(str),
                y=bin_counts.values,
                marker_color='skyblue',
                text=[f"{count}<br>({pct}%)" for count, pct in zip(bin_counts.values, bin_percent.values)],
                textposition='outside'
            ))

            fig.update_layout(
                title=f"Unique Consumers per {x_label}",
                xaxis_title=x_label,
                yaxis_title="Unique Consumer Count",
                autosize=True,
                height=None,
            )

            logs.append(f"✅ Distribution plot generated successfully for attribute {selected_attribute}. ✅ You can also move on to -Clustering Tool- tab on the right ➡️.")
            return fig, html.Ul([html.Li(log) for log in logs])

        except Exception as e:
            logs.append(f"❌ Exception occurred: {str(e)}")
            return go.Figure(), html.Ul([html.Li(log) for log in logs])

    

    @app.callback(
        Output("cluster-graph1", "figure", allow_duplicate=True),
        Output("logs-area1", "children"),
        Input("selected-hours-store1", "data"),
        State("cluster-graph1", "figure"), ## CHANGED
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
    ####### STEP 3 ############## VISUALIZE PLOTS  -- TAB 2
    #############################

    @app.callback(
        Output("store-final-clustered-data", "data"),
        #Output("1visualization-area", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("generate-cluster-graphs1", "n_clicks"),
        State("group-by-options1", "value"),
        State("distance-metric1", "value"),
        State("num-clusters1", "value"),
        State("auto-select-clusters1", "value"),
        State("store-uploaded-file1", "data"),
        prevent_initial_call=True)

    def plot_clusters(gen_button, group_list, distance_metric, number_cluster, opt_cluster_flag, input_data):

        logs = []    
        print("Testing plot_clusters function.....")

        if not any([gen_button, distance_metric, number_cluster, opt_cluster_flag, input_data]):
            return no_update, html.Div("Please Provide all inputs")


        fp = inputfileDirCache.get()  # full path to the uploaded file

        data = pd.DataFrame()
        df = pd.DataFrame()
        db_consumption_cols = []


        if fp.endswith(".csv"):
            data = pd.read_csv(fp)
            df = make_monthly_cons.compute_monthly_consumption(data, consumption_cols=None)
            #logs.append("✅ Reading input csv file.")
        elif fp.endswith(".xls") or fp.endswith(".xlsx"):
            data = pd.read_excel(fp, engine='openpyxl')
            #logs.append("✅ Reading input excel file.")
            df = make_monthly_cons.compute_monthly_consumption(data, consumption_cols= None)
        elif fp.endswith(".duckdb") or fp.endswith(".db"):

            import duckdb
            try:
                # Connect to DuckDB and read all tables or a specific one
                con = duckdb.connect(database=fp, read_only=True)

                # List all tables in the DuckDB file
                tables = con.execute("SHOW TABLES").fetchall()
                logs.append(f"📋 Tables found: {[t[0] for t in tables]}")

                if tables:
                    # Read the first table by default (you can modify this)
                    table_name = tables[0][0]
                    data = con.execute(f"SELECT * FROM {table_name}").fetchdf()
                    data_columns = data.columns
                    # DB Group List


                    matched_sanctioned_load = [c for c in data_columns if any(p in c.lower() for p in CONNECTED_LOAD_PATTERNS)]

                    matched_category = [c for c in data_columns if
                                               any(p in c.lower() for p in CATEGORY_PATTERNS)]

                    matched_consumer_no = [c for c in data_columns if
                                               any(p in c.lower() for p in CONSUMER_PATTERNS)]

                    rename_map = {
                        matched_sanctioned_load[0]: "Sanctioned_Load_KW" if matched_sanctioned_load else None,
                        matched_category[0]: "Category" if matched_category else None,
                        matched_consumer_no[0]: "Consumer No" if matched_consumer_no else None,
                    }

                    # Drop None keys (if some lists were empty)
                    rename_map = {k: v for k, v in rename_map.items() if k is not None}

                    data = data.rename(columns = rename_map)

                    db_consumption_cols = _timeblock_columns(columns=data.columns, TIMEBLOCK_PATTERNS=time_block_patterns)
                    ConsumptionValuesCache.set(db_consumption_cols)

                    df = make_monthly_cons.compute_monthly_consumption(data, consumption_cols=db_consumption_cols)
            except:
                #data = pd.DataFrame()
                logs.append("❌ No tables found in DuckDB file.")


        if not group_list:
            group_list = ['Category', 'Sanctioned_Load_KW', 'monthly_consumption']

        tb_range = TimeBlockRangeCache.get()
        # Retrieve valid time range from cache

        new_df = df.dropna()

        print(f"CLUSTERING DF DIFF is {len(new_df) - len(df)} ROWS")
        clusterer = clustering.ConsumerClusterer(raw_df= new_df,
                                                 group_list=group_list,
                                                 distance_metric = distance_metric,
                                                 opt_flag = opt_cluster_flag,
                                                 num_clusters = number_cluster,
                                                 consumption_cols = db_consumption_cols,
                                                 time_blocks = tb_range)
        
        clusterer.fit()

        final_clustered_data = clusterer.clustered_data
        final_medoid_data = clusterer.medoid_data
        transformed_data = clusterer.reformed_df

        output_file_name = OutputFileNameCache.get()

        ##### SAVE Cluster DATA#######
        cluster_output_path = os.path.join(SaveDirCache.get(), f"{output_file_name}_ToU_Cluster_Results", )
        os.makedirs(cluster_output_path, exist_ok=True)

        final_clustered_data.to_csv(os.path.join(cluster_output_path,"final_clustered_data.csv"))
        final_medoid_data.to_csv(os.path.join(cluster_output_path, "final_medoid_data.csv"))
        transformed_data.to_csv(os.path.join(cluster_output_path, "transformed_data.csv"))

        ClusterfileDirCache.set(cluster_output_path)


        print("3 Testing plot_clusters function.....")

        return {"clustered_data" : final_clustered_data.to_json(date_format='iso', orient='split'), "medoid_data":final_medoid_data.to_json(date_format='iso', orient='split')},html.Div("✅ Clustered data stored! You can either visualize the clusters or Proceed to next steps in Optariff model by selecting Tou Bins")

    #############################
    ####### STEP 4 ############## MAKE DROPDOWNS
    #############################

    @app.callback(
        Output("category-dropdown", "options"),
        #Output("load-bin-dropdown", "options"),
        #Output("consumption-bin-dropdown", "options"),
        Input("store-final-clustered-data", "data"),
        State("group-by-options1", "value"),
        prevent_initial_call=True
    )
    #def populate_dropdowns(clustered_json):
    #def populate_cat_dropdowns(clustered_json):
    def populate_cat_dropdowns(clustered_json, group_list):
        if not clustered_json:
            return [] #, [], []

        print("1 Testing populate_dropdowns function.....")

        if 'Category' in group_list:
        # data = clustered_json.get("clustered_data")
        # clustered_df = pd.read_json(data, orient='split')
            print("1 Testing populate_dropdowns function.....")

            data = clustered_json.get("clustered_data")
            clustered_df = pd.read_json(data, orient='split')

            cat_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['Category'].dropna().unique())]
            return cat_opts
        else:
            return []

        # cat_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['Category'].dropna().unique())]
        #load_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['load_bin'].dropna().unique())]
        #cons_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['consumption_bin'].dropna().unique())]

        #return cat_opts #, load_opts, cons_opts
    
    @app.callback(
        Output("load-bin-dropdown", "options", allow_duplicate=True),
       # Output("consumption-bin-dropdown", "options", allow_duplicate=True),
        Input("category-dropdown", "value"),
        Input("store-final-clustered-data", "data"),
        State("group-by-options1", "value"),
        prevent_initial_call=True
    )
    # def populate_bin_dropdowns(choosen_category,clustered_json):
    #     if not clustered_json or not choosen_category:
    def populate_bin_dropdowns(choosen_category, clustered_json, group_list):
        if not clustered_json or not group_list:
            return []

        print("1 Testing populate_dropdowns function.....")

        data = clustered_json.get("clustered_data")
        clustered_df = pd.read_json(data, orient='split')
        #cluster_sub = clustered_df[clustered_df['Category'] == choosen_category]

        #cat_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['Category'].dropna().unique())]
        #load_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['load_bin'].dropna().unique())]
        #cons_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['consumption_bin'].dropna().unique())]

        #return load_opts

        if 'Category' in group_list:

            if 'Sanctioned_Load_KW' in group_list:
                cluster_sub = clustered_df[clustered_df['Category'] == choosen_category]
                load_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['load_bin'].dropna().unique())]
                return load_opts
            else:
                return []
        else:
            if 'Sanctioned_Load_KW' in group_list:
                load_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['load_bin'].dropna().unique())]
                return load_opts
            else:
                return []

    @app.callback(
        Output("consumption-bin-dropdown", "options", allow_duplicate=True),
        Input("category-dropdown", "value"),
        Input("load-bin-dropdown", "value"),
        Input("store-final-clustered-data", "data"),
        State("group-by-options1", "value"),
        prevent_initial_call=True
    )
    # def populate_cons_dropdowns(choosen_category, choosen_load_bin, clustered_json):
    #     if not clustered_json or not choosen_category or not choosen_load_bin:
    def populate_cons_dropdowns(choosen_category, choosen_load_bin, clustered_json, group_list):
        if not clustered_json or not group_list:
            return []

        print("1 Testing populate_dropdowns function.....")

        data = clustered_json.get("clustered_data")
        clustered_df = pd.read_json(data, orient='split')
        #cluster_sub = clustered_df[(clustered_df['Category'] == choosen_category) & (clustered_df['load_bin'] == choosen_load_bin)]

        # cat_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['Category'].dropna().unique())]
        #load_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['load_bin'].dropna().unique())]
        #cons_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['consumption_bin'].dropna().unique())]

        if 'monthly_consumption' in group_list:
            if 'Category' in group_list:
                if 'Sanctioned_Load_KW' in group_list:
                    cluster_sub = clustered_df[(clustered_df['Category'] == choosen_category) & (clustered_df['load_bin'] == choosen_load_bin)]
                    cons_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['consumption_bin'].dropna().unique())]
                    return cons_opts
                else:
                    cluster_sub = clustered_df[(clustered_df['Category'] == choosen_category)]
                    cons_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['consumption_bin'].dropna().unique())]
                    return cons_opts

            else:
                if 'Sanctioned_Load_KW' in group_list:
                    cluster_sub = clustered_df[(clustered_df['load_bin'] == choosen_load_bin)]
                    cons_opts = [{'label': i, 'value': i} for i in sorted(cluster_sub['consumption_bin'].dropna().unique())]
                    return cons_opts
                else:
                    cons_opts = [{'label': i, 'value': i} for i in sorted(clustered_df['consumption_bin'].dropna().unique())]
                    return cons_opts

        else:
            return []


    #############################
    ####### STEP 5 ############## PLOT
    #############################

    @app.callback(
        Output("cluster-graph1", "figure"),
        Input("category-dropdown", "value"),
        Input("load-bin-dropdown", "value"),
        Input("consumption-bin-dropdown", "value"),
        State("store-final-clustered-data", "data"),

        prevent_initial_call=True
    )
    def plot_based_on_selection(category, load_bin, cons_bin, clustered_json):
        #if not all([category, load_bin, cons_bin, clustered_json]):
        if not clustered_json:
            return no_update

        data1 = clustered_json.get("clustered_data")
        clustered_df = pd.read_json(data1, orient='split')

        data2 = clustered_json.get("medoid_data")
        medoid_df = pd.read_json(data2, orient = 'split')

        # You can reuse your plotting function here
        fig = get_cluster_plot_figure(final_clustered_data = clustered_df,
                                                    final_medoid_data = medoid_df,
                                                    category = category,
                                                    load_bin = load_bin,
                                                    consumption_bin = cons_bin,
                                                      time_blocks = TimeBlockRangeCache.get(),
                                                      consumption_values = ConsumptionValuesCache.get()
                                                      )

        return fig



    #############################
    ####### STEP 4 ############## SELECT TOU DYNAMICITY
    #############################

    @app.callback(
        Output("tou-selection-status1", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("tou-dynamicity-radio1", "value"),
        prevent_initial_call=True
    )
    def store_tou_dynamicity(selection):
        ToUDynamicityCache.set(selection)
        msg = f"✅ ToU dynamicity set to: {selection}"
        return msg, html.Div(msg)
    
    #############################
    ####### STEP 5 ##############
    #############################


    #############################
    ####### STEP 6 ##############
    #############################

    # @app.callback(
    #     Output("selected-hours-store1", "data"),
    #     Output("hour-selection-status1", "children"),
    #     Input("hour-selection1", "value"),
    #     prevent_initial_call=True
    # )
    # def store_selected_hours(selected_hours):
    #     if not selected_hours:
    #         return [], "⚠️ No hours selected."
    #     return selected_hours, f"✅ Selected {len(selected_hours)} hour(s): {sorted(selected_hours)}"

    @app.callback(
        Output("selected-hours-store1", "data"),
        Output("tou-bins-feedback1", "children"),
        Input("confirm-tou-bins1", "n_clicks"),
        State("tou-bins-input1", "value"),
        prevent_initial_call=True
    )
    def confirm_tou_bins(n_clicks, input_text):
        import re
        """Validate and store ToU bin selections."""
        if not input_text:
            return dash.no_update, "⚠️ Please enter at least one time block."

        # Parse numbers (split by comma or pipe)
        parts = re.split(r"[,\|]", input_text)
        try:
            hours = sorted(set(int(p.strip()) for p in parts if p.strip().isdigit()))
        except ValueError:
            return dash.no_update, "❌ Invalid entry: please enter integers only."

        tb_range = TimeBlockRangeCache.get()
        # Retrieve valid time range from cache
        start_hr = tb_range['first']
        end_hr = tb_range['last']

        # Validate range
        invalid = [h for h in hours if h < start_hr or h > end_hr]
        if invalid:
            return dash.no_update, f"❌ Invalid hour(s): {invalid}. Must be within [{start_hr}, {end_hr}]."

        if len(hours) < 2:
            return dash.no_update, "⚠️ You need at least two breakpoints to form bands."

        TouBinsCache.set(hours)
        print(f" [CACHE TEST] Tou Bins Set by user : {TouBinsCache.get()}")
        msg = f"✅ ToU bands updated successfully: {hours}"
        print(f"[INFO] Updated ToU hours: {hours}")
        return hours, msg




    #############################
    ####### STEP 7 ##############
    #############################

    @app.callback(
        Output('continuity-setting1', 'data'),
        Input('keep-continuous-bins1', 'value')
    )
    def update_continuity_setting(value):
        print(f"Continuity Setting is {value}")
        return {'setting': value}

    #############################
    ####### STEP 8 ##############
    #############################

    @app.callback(
        Output("store-param-file1", "data"),
        Output("model-param-upload-status1", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("upload-model-params1", "contents"),
        State("upload-model-params1", "filename"),
        #State("logs-area1", "children"),
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

    from datetime import datetime

    @app.callback(
        Output("logs-area1", "children", allow_duplicate=True),
        Input("run-tou-button1", "n_clicks"),
        State("store-uploaded-file1", "data"),
        State("store-param-file1", "data"),
        State("selected-hours-store1", "data"),
        State('continuity-setting1', 'data'),

        prevent_initial_call=True
    )
    def run_tou_model(n_clicks, input_data, model_param, tou_bins, cont_setting):
        print("Running TOU model callback...")
        # if not n_clicks or not input_data or not model_param:
        #     return no_update


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

        #output_path = SaveDirCache.get()
        #customer_demo = input_data.get("path")

        #from cache import SaveDirCache

        output_folder =  SaveDirCache.get() #ClusterfileDirCache.get()
        clustering_folder =  ClusterfileDirCache.get()
        final_clustered_path = os.path.join(clustering_folder,"final_clustered_data.csv")
        final_medoid_data = os.path.join(clustering_folder, "final_medoid_data.csv")

        model_param_path = model_param.get("path")

        output_file_name = OutputFileNameCache.get()
        
        print("inside tou callback and printing stored file name")
        print(output_file_name)
        bins_tou =sorted(tou_bins)
        cont_set = cont_setting.get("setting")

        if not output_file_name:
            print("No output file name provided. Please confirm the file name before running.")
            sys.stdout = sys_stdout_backup
            return "⚠️ Please confirm the output file name before running the model."
        
        print("inside tou callback and printing stored file name")
        print(output_file_name)
        bins_tou =sorted(tou_bins)
        cont_set = cont_setting.get("setting")

        try:
            print("Starting Model Run .....") 
            new_betrand_cluster_model.run_tou_cluster_model(
                model_param_path = model_param_path,
                output_path = output_folder,
                final_clustered_path = final_clustered_path,
                final_medoid_path = final_medoid_data
                ,tou_bins= bins_tou
                ,total_time_blocks_modelled = 24
                ,cont_setting = cont_set
                ,output_file_name_by_user = output_file_name
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
        Output("trigger-new-tab1", "children"),
        Input("view-optariff-results1", "n_clicks"),
        Input("compare-optariff-results1", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_new_tab(n1, n2):
        triggered_id = ctx.triggered_id
        if triggered_id == "view-optariff-results1":
            return html.Script('window.open("/load-cluster-graphs", "_blank");')
        elif triggered_id == "compare-optariff-results1":
            return html.Script('window.open("/compare-cluster-results", "_blank");')
        return dash.no_update

    