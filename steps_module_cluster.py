# step_modules.py or in your main page file
from dash import html, dcc

#############################
####### STEP 1 ##############
#############################

""" ORIGINAL """
# def step_upload_data():
#     return html.Div(
#         style={"marginBottom": "30px"},
#         children=[
#             html.H4("Step 1: Upload Smart Meter Data"),
#             dcc.Upload(
#                 id="upload-data1",
#                 children=html.Div([
#                     "Drag and drop or ",
#                     html.A("select a file")
#                 ]),
#                 style={
#                     "width": "100%",
#                     "height": "30px",
#                     "lineHeight": "30px",
#                     "borderWidth": "1px",
#                     "borderStyle": "dashed",
#                     "borderRadius": "5px",
#                     "textAlign": "center",
#                     "marginBottom": "10px",
#                     "cursor": "pointer"
#                 },
#                 multiple=False
#             ),
#             dcc.Store(id="store-uploaded-file1"),
#             html.Div(id="file-upload-status1", style={"fontSize": "12px", "color": "green"}),
#             #html.Div(id="log-container"),
#             html.A(
#                 "Download Input File Format",
#                 href="/assets/optariff_input_file_format.csv",
#                 download="optariff_input_file_format.csv",
#                 target="_blank",
#                 style={"fontSize": "13px", "color": "#007BFF", "textDecoration": "underline", "cursor": "pointer"}
#             )
#         ]
#     )


def step_upload_data():
    """Step 1: Choose data source (Excel/CSV or DuckDB) with unified styling."""
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-start",
            "gap": "16px",
            "padding": "24px",
            "borderRadius": "24px",
            "border": "1.167px solid #DAE0E6",
            "background": "#FFF",
            "alignSelf": "stretch",
            "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
            "width": "100%",
            "maxWidth": "600px",
            "margin": "0 auto",
        },
        children=[

            # ---------------------------------------------
            # Header
            # ---------------------------------------------
            html.H4(
                "Step 1: Select Smart Meter Data Source",
                style={"marginBottom": "8px", "color": "#134A94"}
            ),

            # ---------------------------------------------
            # Radio: Data Source Type (file vs duckdb)
            # ---------------------------------------------
            dcc.RadioItems(
                id="data-source-type1",
                options=[
                    {"label": "📁 Upload Excel/CSV", "value": "file"},
                    {"label": "🦆 Use DuckDB File", "value": "duckdb"},
                ],
                value="file",
                labelStyle={"display": "block", "marginBottom": "6px"},
                style={
                    "marginBottom": "12px",
                    "fontSize": "14px",
                    "color": "#333",
                },
            ),

            # ---------------------------------------------
            # Placeholder for Dynamic UI (handled by callback)
            # ---------------------------------------------
            html.Div(id="data-input-area1", style={"width": "100%"}),

            # ---------------------------------------------
            # Download Sample Input
            # ---------------------------------------------
            html.A(
                "📘 Download Sample Input File",
                href="/assets/sample_input_file.csv",
                download="sample_input_file.csv",
                target="_blank",
                style={
                    "fontSize": "14px",
                    "color": "#007BFF",
                    "textDecoration": "underline",
                    "cursor": "pointer",
                    "marginTop": "10px",
                },
            ),

            # Hidden Stores (for callback state)
            dcc.Store(id="store-uploaded-file1"),
            html.Div(id="file-upload-status1"),
            html.Div(id="duckdb-path-status1"),
        ],
    )


#############################
####### STEP 2 ##############
#############################

# def step_select_output_folder():
#     return html.Div([
#     html.H4("Step 2: Select Output Directory"),    
#     html.Button("Select Output Folder", id="select-output-folder-btn1", n_clicks=0, className="btn"),
#     html.Div(id="selected-folder-path1", style={"marginTop": "10px", "fontWeight": "bold", "fontSize": "12px","color": "#333" }),
#     dcc.Store(id="output-folder-store1")
# ])


def step_select_output_folder():
    return html.Div([
        html.H4("Step 2: Select Output Directory"),

        html.Button("Select Output Folder", id="select-output-folder-btn1", n_clicks=0, className="btn"),

        html.Div(
            id="selected-folder-path1",
            style={"marginTop": "10px", "fontWeight": "bold", "fontSize": "12px", "color": "#333"}
        ),

        html.Br(),

        # html.Label("Enter output file name (without extension):", style={"marginTop": "10px"}),
        # dcc.Input(
        #     id="output-file-name-input",
        #     type="text",
        #     placeholder="e.g., optimized_results",
        #     debounce=True,
        #     style={"width": "100%", "marginTop": "5px", "marginBottom": "10px"}
        # ),

        # dcc.Store(id="output-folder-store"),
        # dcc.Store(id="output-file-name-store")

        html.Label("Enter output file name (without extension):", style={"marginTop": "10px"}),
        dcc.Input(
            id="output-file-name-input1",
            type="text",
            placeholder="e.g., optimized_results",
            debounce=True,
            style={"width": "100%", "marginTop": "5px", "marginBottom": "5px"}
        ),
        html.Button("Confirm Output File Name", id="confirm-output-filename-btn1", n_clicks=0, className="btn", style={"marginBottom": "10px"}),

        # Log area for file name confirmation
        html.Div(id="output-file-name-log1", style={"fontSize": "12px", "color": "green"}),

        dcc.Store(id="output-folder-store1"),
        dcc.Store(id="output-file-name-store1")

    ])



#############################
####### STEP 3 ##############
#############################


def step_render_graph():
    return html.Div([
        html.H4("Step 3: View Uploaded Profiles"),
        html.Button("Plot Consumption Profiles", id="plot-consumption-btn1", n_clicks=0, className="btn"),
        dcc.Store(id="consumer-data-store1", storage_type="session")  # store uploaded data
    ])

#############################
####### STEP 3 ##############
#############################

# def view_cluster_tabs():
#     return html.Div([
#         dcc.Tabs([

#             ### First TAB 
#             dcc.Tab(label="Investigate Distribution", children=[
#                 html.Div([
#                     html.H4("Explore Attribute Distribution"),
#                     dcc.Dropdown(
#                         id="distribution-attribute-dropdown1",
#                         options=[
#                             {'label': 'Category', 'value': 'Category'},
#                             {'label': 'Sanctioned Load (KW)', 'value': 'Sanctioned_Load_KW'},
#                             {'label': 'Monthly Consumption', 'value': 'monthly_consumption'}
#                         ],
#                         placeholder="Select Attribute to Investigate",
#                         style={"width": "50%"}
#                     ),
#                     html.Br(),
#                     dcc.Graph(id="distribution-plot1", style={"height": "500px"})
#                 ])
#             ]),

#             ## SECOND TAB
#             dcc.Tab(label="Clustering Tool", children=[
#                 html.Div([
#                     html.H4("Consumer Clustering Setup"),

#                     # Neat row layout with colored boxes
#                     html.Div([
#                         html.Div([
#                             html.Label("Group By:", style={'font-size': '12px'}),
#                             dcc.Checklist(
#                                 id='group-by-options1',
#                                 options=[
#                                     {'label': 'Category', 'value': 'Category'},
#                                     {'label': 'Sanctioned Load', 'value': 'Sanctioned_Load_KW'},
#                                     {'label': 'Monthly Consumption', 'value': 'monthly_consumption'}
#                                 ],
#                                 value=[],
#                                 labelStyle={'display': 'block', 'font-size': '12px'}
#                             )
#                         ], style={
#                             'backgroundColor': '#f0f8ff',
#                             'border': '1px solid #ccc',
#                             'borderRadius': '5px',
#                             'padding': '10px',
#                             'margin-right': '10px',
#                             'font-size': '12px',
#                             'width': '16%'
#                         }),

#                         html.Div([
#                             html.Label("Distance Metric:", style={'font-size': '12px'}),
#                             dcc.Dropdown(
#                                 id='distance-metric1',
#                                 options=[
#                                     {'label': 'Euclidean', 'value': 'euclidean'},
#                                     {'label': 'DTW', 'value': 'dtw'},
#                                     {'label': 'Cosine', 'value': 'cosine'}
#                                 ],
#                                 placeholder="Select",
#                                 style={"width": "100%", 'font-size': '12px'}
#                             )
#                         ], style={
#                             'backgroundColor': '#f0f8ff',
#                             'border': '1px solid #ccc',
#                             'borderRadius': '5px',
#                             'padding': '10px',
#                             'margin-right': '10px',
#                             'width': '16%'
#                         }),

#                         html.Div([
#                             html.Label("No. of Clusters:", style={'font-size': '12px'}),
#                             dcc.Dropdown(
#                                 id='num-clusters1',
#                                 options=[{'label': str(i), 'value': i} for i in range(2, 11)],
#                                 placeholder="Select",
#                                 style={"width": "100%", 'font-size': '12px'}
#                             )
#                         ], style={
#                             'backgroundColor': '#f0f8ff',
#                             'border': '1px solid #ccc',
#                             'borderRadius': '5px',
#                             'padding': '10px',
#                             'margin-right': '10px',
#                             'width': '16%'
#                         }),

#                         html.Div([
#                             html.Label("Auto-select Clusters?", style={'font-size': '12px'}),
#                             dcc.Dropdown(
#                                 id='auto-select-clusters1',
#                                 options=[
#                                     {'label': 'Yes', 'value': 'yes'},
#                                     {'label': 'No', 'value': 'no'}
#                                 ],
#                                 placeholder="Yes / No",
#                                 style={"width": "100%", 'font-size': '12px'}
#                             )
#                         ], style={
#                             'backgroundColor': '#f0f8ff',
#                             'border': '1px solid #ccc',
#                             'borderRadius': '5px',
#                             'padding': '10px',
#                             'margin-right': '10px',
#                             'width': '16%'
#                         }),

#                         html.Div([
#                             html.Label(""),
#                             html.Button("Generate & View Cluster Graphs", id='generate-cluster-graphs1', n_clicks=0,
#                                         style={'font-size': '12px', 'margin-top': '18px'})
#                         ], style={
#                             'backgroundColor': '#f0f8ff',
#                             'border': '1px solid #ccc',
#                             'borderRadius': '5px',
#                             'padding': '10px',
#                             'width': '16%'
#                         })

#                     ], style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'nowrap'}),

#                     html.Hr(),

#                     # Graph display
#                     dcc.Graph(id="cluster-graph1", style={"height": "500px"})
#                 ])
#             ])
#         ])
#     ])

def view_cluster_tabs():
    return html.Div([
        dcc.Tabs([

            ### First TAB 
            dcc.Tab(label="Investigate Distribution", children=[
                html.Div([
                    html.H3("Explore Attribute Distribution"),
                    dcc.Dropdown(
                        id="distribution-attribute-dropdown1",
                        options=[
                            {'label': 'Category', 'value': 'Category'},
                            {'label': 'Sanctioned Load (KW)', 'value': 'Sanctioned_Load_KW'},
                            {'label': 'Monthly Consumption', 'value': 'monthly_consumption'}
                        ],
                        placeholder="Select Attribute to Investigate",
                        style={"width": "50%"}
                    ),
                    html.Br(),
                    dcc.Graph(id="distribution-plot1", style={"height": "500px"})
                ])
            ]),

            ## SECOND TAB
            dcc.Tab(label="Clustering Tool", children=[
                html.Div([
                    html.H3("Consumer Clustering Setup"),

                    # Neat row layout with colored boxes
                    html.Div([
                        html.Div([
                            html.Label("Group By:", style={'font-size': '12px'}),
                            dcc.Checklist(
                                id='group-by-options1',
                                options=[
                                    {'label': 'Category', 'value': 'Category'},
                                    {'label': 'Sanctioned Load', 'value': 'Sanctioned_Load_KW'},
                                    {'label': 'Monthly Consumption', 'value': 'monthly_consumption'}
                                ],
                                value=[],
                                labelStyle={'display': 'block', 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f0f8ff',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'margin-right': '10px',
                            'font-size': '12px',
                            'width': '16%'
                        }),


                        html.Div([
                            html.Label("Distance Metric:", style={'font-size': '12px'}),
                            dcc.Dropdown(
                                id='distance-metric1',
                                options=[
                                    {'label': 'Euclidean', 'value': 'euclidean'},
                                    # {'label': 'DTW', 'value': 'dtw'},
                                    # {'label': 'Cosine', 'value': 'cosine'}
                                    {'label': 'Cityblock', 'value': 'cityblock'},
                                    {'label': 'Cosine', 'value': 'cosine'},
                                    {'label': 'Manhattan', 'value': 'manhattan'}
                                ],
                                placeholder="Select",
                                style={"width": "100%", 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f0f8ff',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'margin-right': '10px',
                            'width': '16%'
                        }),

                        html.Div([
                            html.Label("No. of Clusters:", style={'font-size': '12px'}),
                            dcc.Dropdown(
                                id='num-clusters1',
                                options=[{'label': str(i), 'value': i} for i in range(2, 11)],
                                placeholder="Select",
                                style={"width": "100%", 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f0f8ff',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'margin-right': '10px',
                            'width': '16%'
                        }),

                        html.Div([
                            html.Label("Auto-select Clusters?", style={'font-size': '12px'}),
                            dcc.Dropdown(
                                id='auto-select-clusters1',
                                options=[
                                    {'label': 'Yes', 'value': 'yes'},
                                    {'label': 'No', 'value': 'no'}
                                ],
                                placeholder="Yes / No",
                                style={"width": "100%", 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f0f8ff',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'margin-right': '10px',
                            'width': '16%'
                        }),

                        html.Div([
                            html.Label(""),
                            html.Button("Generate & View Cluster Graphs", id='generate-cluster-graphs1', n_clicks=0,
                                        style={'font-size': '12px', 'margin-top': '18px'})
                        ], style={
                            'backgroundColor': '#f0f8ff',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'width': '16%'
                        })

                    ], style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'nowrap'}),

                    html.Div([
                        html.Div([
                            html.Label("Category", style={'font-size': '12px'}),
                            dcc.Dropdown(
                                id='category-dropdown',
                                options=[],  # to be populated dynamically
                                placeholder="Select Category",
                                style={'width': '100%', 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f9f9f9',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'margin-right': '10px',
                            'width': '20%'
                        }),

                        html.Div([
                            html.Label("Load Bin", style={'font-size': '12px'}),
                            dcc.Dropdown(
                                id='load-bin-dropdown',
                                options=[],  # to be populated dynamically
                                placeholder="Select Load Bin",
                                style={'width': '100%', 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f9f9f9',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'margin-right': '10px',
                            'width': '20%'
                        }),

                        html.Div([
                            html.Label("Monthly Consumption Bin", style={'font-size': '12px'}),
                            dcc.Dropdown(
                                id='consumption-bin-dropdown',
                                options=[],  # to be populated dynamically
                                placeholder="Select Consumption Bin",
                                style={'width': '100%', 'font-size': '12px'}
                            )
                        ], style={
                            'backgroundColor': '#f9f9f9',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'padding': '10px',
                            'width': '20%'
                        }),

                    ], style={'display': 'flex', 'flexDirection': 'row', 'marginTop': '10px'}),

                    html.Hr(),

                    # Graph display
                    dcc.Graph(id="cluster-graph1", style={"height": "500px"})
                ])
            ])
        ])
    ])




#############################
####### STEP 4 ##############
#############################

def step_select_tou_dynamicity():
    return html.Div([
        html.H4("Step 3: Select ToU Dynamicity"),
        dcc.RadioItems(
            id="tou-dynamicity-radio1",
            options=[
                {"label": "Month", "value": "Month"},
                {"label": "Season", "value": "Season"},
            ],
            value="Month",  # default selection
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        ),
        html.Div(id="tou-selection-status1", style={"marginTop": "10px", "color": "#555"}),
    ])


#############################
####### STEP 5 ##############
#############################

# def step_select_representative_profile():
#     return html.Div([
#         html.H4("Step 4: Get Representative Profile"),
#         html.Button("Get Representative Profile", id="get-rep-profile-btn", n_clicks=0, className="btn"),
#         html.Div(id="rep-profile-status", style={"marginTop": "10px", "fontSize": "13px", "color": "#555"}),
#         # No graph here, graph goes to 'visualization-area' in main layout
        
#     ])

#############################
####### STEP 6 ##############
#############################

""" Original """
# def select_tou_bins():
#     return html.Div([
#         html.H4("Step 3: Select ToU Bins"),
#
#         dcc.Checklist(
#             id="hour-selection1",
#             options=[{"label": str(i), "value": i} for i in range(1, 25)],
#             value=[],
#             labelStyle={"display": "inline-block", "margin-right": "10px", "margin-bottom": "5px"}
#         ),
#
#         html.Br(),
#         html.Div(id="hour-selection-status1", style={"margin-top": "10px", "fontWeight": "bold"}),
#
#         # Store for selected hour range
#         dcc.Store(id="selected-hours-store", storage_type="session")
#     ])


def select_tou_bins():
    return html.Div([
        html.H4("Step 3: Define ToU Bins", style={"marginBottom": "10px"}),

        html.Div([
            html.Label("Enter Time Blocks (comma or | separated):",
                       style={"fontWeight": "600", "marginBottom": "5px"}),
            dcc.Input(
                id="tou-bins-input1",
                type="text",
                placeholder="e.g., 1, 2, 3, 48 or 1|3|5|48",
                debounce=False,  # ✅ user must click confirm
                style={
                    "width": "100%",
                    "padding": "8px",
                    "border": "1px solid #ccc",
                    "borderRadius": "6px",
                }
            ),
            html.Button(
                "Confirm ToU Bands",
                id="confirm-tou-bins1",
                n_clicks=0,
                style={
                    "marginTop": "10px",
                    "background": "#134A94",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "6px",
                    "padding": "6px 14px",
                    "cursor": "pointer"
                }
            ),
        ]),

        html.Div(id="tou-bins-feedback1", style={"marginTop": "10px", "color": "#134A94"}),

        dcc.Store(id="selected-hours-store1", storage_type="session"),
    ])


#############################
####### STEP 7 ##############
#############################

def first_last_continuity():
    return html.Div([
    html.H4("Step 4: Option to keep first & last continous? "),
    #html.Label("Keep first and last bins continuous?"),
    dcc.RadioItems(
        id='keep-continuous-bins1',
        options=[
            {'label': 'Yes', 'value': 'yes'},
            {'label': 'No', 'value': 'no'}
        ],
        value='yes',  # default value
        labelStyle={'display': 'inline-block', 'margin-right': '20px'}
    )
])

#############################
####### STEP 8 ############## Read Model Parameter File
#############################

def step_upload_model_param():
    return html.Div(
        style={"marginBottom": "30px"},
        children=[
            html.H4("Step 5: Upload Model Parameters"),
            dcc.Upload(
                id="upload-model-params1",
                children=html.Div([
                    "Drag and drop or ",
                    html.A("select a file")
                ]),
                style={
                    "width": "100%",
                    "height": "30px",
                    "lineHeight": "30px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "marginBottom": "10px",
                    "cursor": "pointer"
                },
                multiple=False
            ),
            dcc.Store(id="store-param-file1"),
            html.Div(id="model-param-upload-status1", style={"fontSize": "12px", "color": "green"}),
            #html.Div(id="log-container"),
            html.A(
                "Download Optariff Model Parameter File Format",
                href="/assets/OPTARIFF_model_parameter_file_FORMAT.xlsx",
                download="OPTARIFF_model_parameter_file_FORMAT.xlsx",
                target="_blank",
                style={"fontSize": "13px", "color": "#007BFF", "textDecoration": "underline", "cursor": "pointer"}
            )
        ]
    )



#############################
####### STEP 9 ############## RUN Model
#############################

def step_run_model():
    return html.Div([
        html.H4("Step 6: Run Optariff for Clustered Consumers"),
        html.Button("Run Optariff", id="run-tou-button1",
                                    n_clicks=0,
                                    className="btn" ),     
    ])
            


#############################
####### STEP 10 ############## View results
#############################

# def step_view_results():
#     return   html.Div([ html.H4("Step 7: View Results"),
#                                  html.Button("View Results", id="view-optariff-results1",
#                                     n_clicks=0,
#                                     className="btn" ), 
#     ])
                


def step_view_results():
    return html.Div([
        html.H4("Step 7: View Results"),

        html.Div([
            html.A(
                html.Button("View Current Results", className="btn"),
                href="/load-cluster-graphs",
                target="_blank",
                id="view-optariff-results1"
            ),
            html.A(
                html.Button("Compare Existing Results", className="btn", style={'margin-left': '10px'}),
                href="/compare-cluster-results",
                target="_blank",
                id="compare-optariff-results1"
            )
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'justifyContent': 'start',
            'alignItems': 'center',
            'margin-top': '10px'
        })
    ])
