# step_modules.py or in your main page file
from dash import html, dcc

#############################
####### STEP 1 ##############
#############################




from dash import html, dcc

# def step_upload_data():
#     """Step 1: Choose data source (Excel/CSV or DuckDB) with unified styling."""
#     return html.Div(
#         style={
#             "display": "flex",
#             "flexDirection": "column",
#             "alignItems": "flex-start",
#             "gap": "16px",
#             "padding": "24px",
#             "borderRadius": "24px",
#             "border": "1.167px solid #DAE0E6",
#             "background": "#FFF",
#             "alignSelf": "stretch",
#             "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
#             "width": "100%",
#             "maxWidth": "600px",
#             "margin": "0 auto",
#         },
#         children=[

#             # ---------------------------------------------
#             # Header
#             # ---------------------------------------------
#             html.H4("Step 1: Select Smart Meter Data Source", style={"marginBottom": "8px"}),

#             # ---------------------------------------------
#             # Radio: Data Source Type
#             # ---------------------------------------------
#             dcc.RadioItems(
#                 id="data-source-type",
#                 options=[
#                     {"label": "Upload Excel/CSV", "value": "file"},
#                     {"label": "Use DuckDB File", "value": "duckdb"},
#                 ],
#                 value="file",
#                 # labelStyle={"display": "block", "marginBottom": "6px"},
#                 # style={
#                 #     "marginBottom": "12px",
#                 #     "fontSize": "13px",
#                 #     "color": "#333",
#                 # },
#             ),

#             # ---------------------------------------------
#             # Placeholder for Upload/Selection UI (dynamic)
#             # ---------------------------------------------
#             html.Div(id="data-input-area"),

#             # ---------------------------------------------
#             # Download Sample Input Link
#             # ---------------------------------------------
#             html.A(
#                 "📘 Download Sample Input File",
#                 href="/assets/sample_input_file.csv",
#                 download="sample_input_file.csv",
#                 target="_blank",
#                 style={
#                     "fontSize": "14px",
#                     "color": "#007BFF",
#                     "textDecoration": "underline",
#                     "cursor": "pointer",
#                     "marginTop": "10px",
#                 },
#             ),
#         ],
#     )

from dash import html, dcc

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
                id="data-source-type",
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
            html.Div(id="data-input-area", style={"width": "100%"}),

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
            dcc.Store(id="store-uploaded-file"),
            html.Div(id="file-upload-status"),
            html.Div(id="duckdb-path-status"),
        ],
    )


#############################
####### STEP 2 ##############
#############################



def step_select_output_folder():
    return html.Div([
        html.H4("Step 2: Select Output Directory"),

        html.Button("Select Output Folder", id="select-output-folder-btn", n_clicks=0, className="btn"),

        html.Div(
            id="selected-folder-path",
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
            id="output-file-name-input",
            type="text",
            placeholder="e.g., optimized_results",
            debounce=True,
            style={"width": "100%", "marginTop": "5px", "marginBottom": "5px"}
        ),
        html.Button("Confirm Output File Name", id="confirm-output-filename-btn", n_clicks=0, className="btn", style={"marginBottom": "10px"}),

        # Log area for file name confirmation
        html.Div(id="output-file-name-log", style={"fontSize": "12px", "color": "green"}),

        dcc.Store(id="output-folder-store"),
        dcc.Store(id="output-file-name-store")

    ])


#############################
####### STEP 3 ##############
#############################


def step_render_graph():
    return html.Div([
        html.H4("Step 3: View Uploaded Profiles"),
        html.Button("Plot Consumption Profiles", id="plot-consumption-btn", n_clicks=0, className="btn"),
        dcc.Store(id="consumer-data-store", storage_type="session")  # store uploaded data
    ])

#############################
####### STEP 3 ##############
#############################

from dash import html, dcc

def view_customer_profile():
    """Visualization area UI: filters + graph."""
    return html.Div([
        html.Div([
            html.H5("Consumer Profile Viewer", style={"color": "#134A94", "marginBottom": "10px"}),

            # Consumer dropdown
            html.Label("Select Consumer No:", style={"fontWeight": "600"}),
            dcc.Dropdown(
                id="consumer-dropdown",
                placeholder="Select Consumer No",
                searchable=True,
                clearable=True,
                # debounce=True,      # prevents firing every keystroke
                style={"marginBottom": "15px"}
            ),

            # Month dropdown (disabled until consumer selected)
            html.Label("Select Month:", style={"fontWeight": "600"}),
            dcc.Dropdown(
                id="month-dropdown",
                placeholder="Select Month",
                disabled=True,
                style={"marginBottom": "15px"}
            ),

            # Button for representative profile
            html.Button(
                "View Representative Profile",
                id="btn-view-rep-profile",
                n_clicks=0,
                style={
                    "marginTop": "10px",
                    "marginBottom": "15px",
                    "backgroundColor": "#007BFF",
                    "color": "white",
                    "fontWeight": "600",
                    "borderRadius": "5px",
                    "padding": "8px 15px",
                    "border": "none",
                    "cursor": "pointer"
                }
            ),

        ], style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "10px",
            "marginBottom": "15px"
        }),

        dcc.Graph(id="profile-graph", style={"height": "450px"}),
        html.Div(id="profile-info", style={"marginTop": "10px", "fontSize": "13px", "color": "#333"})
    ])




#############################
####### STEP 4 ##############
#############################

def step_select_tou_dynamicity():
    return html.Div([
        html.H4("Step 3: Select ToU Dynamicity"),
        dcc.RadioItems(
            id="tou-dynamicity-radio",
            options=[
                {"label": "Month", "value": "Month"},
                {"label": "Season", "value": "Season"},
            ],
            value="Month",  # default selection
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        ),
        html.Div(id="tou-selection-status", style={"marginTop": "10px", "color": "#555"}),
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



# def select_tou_bins():
#     return html.Div([
#         html.H4("Step 3: Select ToU Bins"),

#         html.Label("Enter ToU Hour Blocks (comma or | separated):", 
#                    style={"fontWeight": "600", "marginBottom": "6px"}),

#         dcc.Input(
#             id="tou-bins-input",
#             type="text",
#             placeholder="e.g. 1, 2, 3 | 12,13,14 | 20-23",
#             style={
#                 "width": "100%",
#                 "padding": "8px 12px",
#                 "border": "1px solid #ccc",
#                 "borderRadius": "8px",
#                 "marginBottom": "10px"
#             },
#         ),

#         html.Button(
#             "Confirm Bins", 
#             id="confirm-tou-bins-btn", 
#             n_clicks=0,
#             style={
#                 "backgroundColor": "#134A94",
#                 "color": "white",
#                 "border": "none",
#                 "padding": "8px 16px",
#                 "borderRadius": "6px",
#                 "cursor": "pointer",
#                 "marginBottom": "10px"
#             },
#         ),

#         html.Div(
#             id="hour-selection-status",
#             style={"marginTop": "8px", "fontWeight": "bold"}
#         ),

#         # Store for parsed hour bins
#         dcc.Store(id="selected-hours-store", storage_type="session")
#     ])

def select_tou_bins():
    return html.Div([
        html.H4("Step 3: Define ToU Bins", style={"marginBottom": "10px"}),

        html.Div([
            html.Label("Enter Time Blocks (comma or | separated):",
                       style={"fontWeight": "600", "marginBottom": "5px"}),
            dcc.Input(
                id="tou-bins-input",
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
                id="confirm-tou-bins",
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

        html.Div(id="tou-bins-feedback", style={"marginTop": "10px", "color": "#134A94"}),

        dcc.Store(id="selected-hours-store", storage_type="session"),
    ])



#############################
####### STEP 7 ##############
#############################

def first_last_continuity():
    return html.Div([
    html.H4("Step 4: Option to keep first & last continous? "),
    #html.Label("Keep first and last bins continuous?"),
    dcc.RadioItems(
        id='keep-continuous-bins',
        options=[
            {'label': 'Yes', 'value': 1},
            {'label': 'No', 'value': 0}
        ],
        value=1,  # default value
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
                id="upload-model-params",
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
            dcc.Store(id="store-param-file"),
            html.Div(id="model-param-upload-status", style={"fontSize": "12px", "color": "green"}),
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
        html.H4("Step 6: Run Optariff for Individual Consumers"),
        html.Button("Run Optariff", id="run-tou-button",
                                    n_clicks=0,
                                    className="btn" ), 
        #dcc.Interval(id="log-interval", interval=1000, n_intervals=0, disabled=True),  # 1 sec interval    
    ])
            


#############################
####### STEP 10 ############## View results
#############################

# def step_view_results():
#     return   html.Div([ html.A("Step 8: View Results"),
#                                  html.Button("View Results", id="view-optariff-results",
#                                     n_clicks=0,
#                                     className="btn" ), 
#     ])

# html.A("View Load Shift Graphs", href="/load-graphs",  # this is the internal URL
#        target="_blank"          


# def step_view_results():
#     return html.Div([
#         html.H4("Step 8: View Results"),
#         html.Button("View Results", id="view-optariff-results", n_clicks=0, className="btn"),
#         dcc.Location(id="redirect1", refresh=True)
#     ])

# def step_view_results():
#     return html.Div([
#         html.H4("Step 7: View Results"),
#         html.A(
#             html.Button("View Results", className="btn"),
#             href="/load-graphs",
#             target="_blank",  # Ensures it opens in a new tab
#             id="view-optariff-results-link"
#         )
#     ])


def step_view_results():
    return html.Div([
        html.H4("Step 7: View Results"),

        html.Div([
            html.A(
                html.Button("View Current Results", className="btn"),
                href="/load-graphs",
                target="_blank",
                id="view-optariff-results-link"
            ),
            html.A(
                html.Button("Compare Existing Results", className="btn", style={'margin-left': '10px'}),
                href="/compare-results",
                target="_blank",
                id="compare-optariff-results-link"
            )
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'justifyContent': 'start',
            'alignItems': 'center',
            'margin-top': '10px'
        })
    ])
