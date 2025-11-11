import dash
from dash import dcc, html
from dash import dcc, html, Input, Output, State, no_update

from pages.cache import SaveDirCache , OutputFileNameCache
import os
import pandas as pd


layout = html.Div([

    html.H1("Optariff: Cluster Model Results", style={"textAlign": "center", "marginBottom": "30px"}),

    # Tabs
    dcc.Tabs(id='view-results-tabs1', value='tab-consumer', children=[
        dcc.Tab(label='Consumer', value='tab-consumer'),
        dcc.Tab(label='Cluster', value='tab-cluster'),
        dcc.Tab(label='Total', value='tab-total'),
    ]),

    # This part will update dropdowns depending on active tab
    html.Div(id='view-results-dropdown-area1', children=[], style={'margin': '20px 0'}),

    # Graph area
    html.Div(
        dcc.Graph(
            id='view-results-graph1',
            config={'responsive': True},
            style={'height': '80vh', 'width': '90%', 'margin': '0 auto'}
        )
    ),

    html.Div(id='view-results-loading-warning1', style={'color': 'red', 'marginTop': '10px'})

], style={'padding': '20px'})





def register_callbacks(app):

    @app.callback(
        Output('view-results-dropdown-area1', 'children'),
        Input('view-results-tabs1', 'value')
    )
    def update_dropdown_area(selected_tab):
        if selected_tab == 'tab-consumer':
            return [
                html.Label("Select Consumer"),
                dcc.Dropdown(id='consumer-dropdown1', placeholder="Select a Consumer", style={'width': '50%'})
            ]

        elif selected_tab == 'tab-cluster':
            return [
                # html.Label("Select Category"),
                # dcc.Dropdown(id='category-dropdown1', placeholder="Select Category", style={'width': '50%'}),

                # html.Label("Select Sanctioned Load Bin"),
                # dcc.Dropdown(id='load-bin-dropdown1', placeholder="Select Load Bin", style={'width': '50%'}),

                # html.Label("Select Consumption Bin"),
                # dcc.Dropdown(id='consumption-bin-dropdown1', placeholder="Select Consumption Bin", style={'width': '50%'}),

                # html.Label("Select Cluster"),
                # dcc.Dropdown(id='cluster-dropdown1', placeholder="Select Cluster", style={'width': '50%'})
                html.Div([

        html.Div([
            html.Label("Select Category"),
            dcc.Dropdown(id='category-dropdown1', placeholder="Select Category", style={'width': '100%'}),
        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Sanctioned Load Bin"),
            dcc.Dropdown(id='load-bin-dropdown1', placeholder="Select Load Bin", style={'width': '100%'}),
        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Consumption Bin"),
            dcc.Dropdown(id='consumption-bin-dropdown1', placeholder="Select Consumption Bin", style={'width': '100%'}),
        ], style={'width': '23%', 'marginRight': '1%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Cluster"),
            dcc.Dropdown(id='cluster-dropdown1', placeholder="Select Cluster", style={'width': '100%'}),
        ], style={'width': '23%', 'display': 'inline-block'}),

    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'marginBottom': '10px'})
            ]

        elif selected_tab == 'tab-total':
            return []  # No dropdowns

        return []


    @app.callback(
        Output('consumer-dropdown1', 'options'),
        Output('view-results-loading-warning1', 'children'),
        Input('consumer-dropdown1', 'id')   # dummy trigger
    )
    def populate_cat(_):
        
        #save_dir = tou_data.get("save_dir")
        #save_directory = run_model_dashboard.get_save_dir()
        
        save_directory = SaveDirCache.get()
        output_file_name_str = OutputFileNameCache.get()  # Store in cache

        print("in load shift populating consumer no")
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


