from dash import html, dcc, Output, Input, callback, Dash
from steps_module_cluster import step_upload_data, step_select_output_folder , view_cluster_tabs , step_select_tou_dynamicity, select_tou_bins, first_last_continuity, step_upload_model_param, step_run_model, step_view_results
import dash
import plotly.graph_objs as go
from pages.cache import inputfileDirCache , SaveDirCache , ToUDynamicityCache , RepProfileCache , model_param_Cache , OutputFileNameCache, ClusterfileDirCache
import sys
from sklearn.ensemble import IsolationForest
import pages
from pages import make_monthly_cons
from pages.plot_clusters import get_cluster_plot_figure
from pages import clustering
from dash.exceptions import PreventUpdate
from pages import new_betrand_cluster_model
from dash import html, dcc, ctx


## Logic is as follows:
# 1. User uploads data. if he isn't sure of format, he can download and see required format
# 2. User can now start visualizing from first tab, he can now explore the attribute distribution to help guide clustering
# 3. User can then select clustering options
# 4. Then, remaining is as per run individual model



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

    @app.callback(
        Output("store-uploaded-file1", "data"),
        Output("file-upload-status1", "children"),
        Output("logs-area1", "children", allow_duplicate=True),
        Input("upload-data1", "contents"),
        State("upload-data1", "filename"),
        #State("logs-area1", "children"),
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
                html.Div(f"✅ Uploaded file: {filename}."),
                html.Div(f"✅ File {filename} is ready to visualize. ‼️ Please select Ouput Directory before visualizing and then Select options in *Investigate Distribution* and  *Clustering Tool tabs* on the right-hand-side panel.")
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

            if selected_attribute not in df.columns and selected_attribute not in ['Sanctioned_Load_KW', 'monthly_consumption']:
                logs.append(f"❌ Selected attribute '{selected_attribute}' not found in data.")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            # Handle binning logic
            if selected_attribute == 'Sanctioned_Load_KW':
                if 'sanctioned_load_bin' not in df.columns:
                    #bins = [0, 1, 2, 3, 5, 10, 20, 50, 100, float('inf')]
                    #labels = ['0-1', '1-2', '2-3', '3-5', '5-10', '10-20', '20-50', '50-100', '100+']
                    
                    df['sanctioned_load_bin'] = pd.qcut(df['Sanctioned_Load_KW'], q=10, duplicates='drop')
                    
                    #df['sanctioned_load_bin'] = pd.cut(df['Sanctioned_Load_KW'], bins=bins, labels=labels, right=False)
                    logs.append("📊 Created sanctioned load bins.")
                group_col = 'sanctioned_load_bin'
                x_label = 'Sanctioned Load Bin (kW)'

            elif selected_attribute == 'monthly_consumption':
                
                consumption_cols = [col for col in df.columns if col.startswith('Consumption_Hr_')]
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

                
                monthly_consumption_df = df.groupby(['Consumer No', 'Month', 'Year'])['daily_demand'].sum().reset_index(name='total_monthly_consumption')
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
                    df = df.merge(monthly_consumption_df[['Consumer No', 'Year', 'Month', 'total_monthly_consumption']], on=['Consumer No', 'Year', 'Month'], how='left')

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

            else:
                group_col = selected_attribute
                x_label = selected_attribute


            # Frequency stats
            if 'Consumer No' not in df.columns:
                logs.append("❌ 'Consumer No' column missing from file.")
                return go.Figure(), html.Ul([html.Li(log) for log in logs])

            bin_counts = df.groupby(group_col)['Consumer No'].nunique().sort_index()
            total_unique = df['Consumer No'].nunique()
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

        #if not any([gen_button, group_list, distance_metric, number_cluster, opt_cluster_flag, input_data]):
        #    return no_update

        if not any([gen_button, distance_metric, number_cluster, opt_cluster_flag, input_data]):
            return no_update, html.Div("Please Provide all inputs")


        #data = pd.read_csv(input_data.get("path"))

        fp = inputfileDirCache.get()  # full path to the uploaded file

        if fp.endswith(".csv"):
            data = pd.read_csv(fp)
            #logs.append("✅ Reading input csv file.")
        elif fp.endswith(".xls") or fp.endswith(".xlsx"):
            data = pd.read_excel(fp, engine='openpyxl')
            #logs.append("✅ Reading input excel file.")
        #else:
            #logs.append("❌ Unsupported file format.")
            #return go.Figure(), html.Ul([html.Li(log) for log in logs])



        df = make_monthly_cons.compute_monthly_consumption(data)

        if not group_list:
            group_list = ['Category', 'Sanctioned_Load_KW', 'monthly_consumption']

        print("2 Testing plot_clusters function.....")

        #clusterer = clustering.ConsumerClusterer(raw_df=df, group_list=group_list, distance_metric = distance_metric)
        
        clusterer = clustering.ConsumerClusterer(raw_df=df, group_list=group_list, distance_metric = distance_metric,
                                                 opt_flag = opt_cluster_flag, num_clusters = number_cluster)
        
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
                                                    consumption_bin = cons_bin)

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

    @app.callback(
        Output("selected-hours-store1", "data"),
        Output("hour-selection-status1", "children"),
        Input("hour-selection1", "value"),
        prevent_initial_call=True
    )
    def store_selected_hours(selected_hours):
        if not selected_hours:
            return [], "⚠️ No hours selected."
        return selected_hours, f"✅ Selected {len(selected_hours)} hour(s): {sorted(selected_hours)}"
    

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

    