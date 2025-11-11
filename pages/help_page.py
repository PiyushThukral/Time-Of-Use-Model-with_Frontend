import dash
import os
import sys
import base64
from dash import dcc, html
from dash.dependencies import Input, Output

stellar_notification = html.Div(
    [
        html.Div(
            [
                # Left side with text
                html.Span(
                    "Stellar is Currently Running",
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
                            "widht": "6vw",
                        },
                    ),
                    html.H2("Stellar"),
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
                            src="assets/Input Dash icon.png",
                            style={
                                "height": "3vh",
                                "width": "1.5vw",
                            },
                        ),
                        html.Button(
                            "Input Dashboard",
                            style={
                                "border": "none",
                                "background": "#E6F0F9",
                                "cursor": "pointer",
                                "padding": "0",
                            },
                        ),
                    ],
                ),
                href="/input-dashboard",
                style={"text-decoration": "none"},
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
            html.Div(
                style={
                    "margin-top": "2.5vh",
                    "display": "flex",
                    "align-items": "center",
                    "width": "10vw",
                    "border": "none",
                    "border-radius": "5px",
                    "height": "4vh",
                    "left": "52%",
                    "transform": "translateX(-50%)",
                    "padding": "5px",
                    "paddingLeft": "10px",
                    "color": "#134A94",
                    "background": "#FFFFFF",
                    "gap": "0.5vw",
                    "position": "absolute",
                    "bottom": "25vh",
                },
                children=[
                    html.Img(
                        src="assets/help icon blue.png",
                        style={
                            "height": "3vh",
                            "width": "1.5vw",
                        },
                    ),
                    html.Button(
                        "Help",
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

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
        dcc.Download(id="download-pdf"),
        stellar_notification,
        html.Div(
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
                        "height": "50px",
                        "width": "280px",
                        "margin-left": "30px",
                    },
                ),
            ],
        ),
        html.Div(
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
            },
            children=sidebar_children,
        ),
        html.Div(
            style={
                "position": "absolute",
                "top": "10vh",
                "left": "13vw",
                "width": "calc(100vw - 13vw)",
                "height": "calc(87vh - 0vh)",
                "display": "flex",
                "flex-direction": "column",
                "alignItems": "center",
                "overflowX": "auto",
                "overflowY": "auto",
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": "#FFFFFF",
                        "border": "1px solid #D1D5DB",
                        "width": "80vw",
                        "display": "flex",
                        "flex-direction": "column",
                        "alignItems": "center",
                        "borderRadius": "10px",
                        "marginTop": "20px",
                    },
                    children=[
                        html.Div(
                            style={"textAlign": "center", "padding": "16px"},
                            children=[
                                html.H3(
                                    "This Coordinated Generation, Transmission, and Storage Expansion Planning Model with endogenous Demand Response and Resource Adequacy has been developed ",
                                    style={"marginTop": 0, "fontSize": "20px"},
                                ),
                                html.Div(
                                    children = [
                                    html.Div(
                                        style={"marginTop": "10px", "fontSize": "16px", "textAlign": "left"},
                                        children=[
                                            html.H4("Under the guidance of CEA: "),
                                            html.P("Shri Ghanshyam Prasad, Chairperson CEA"),
                                            html.P("Shri A. Balan, Member Planning CEA"),
                                            html.P("Shri Vijay Menghani, CE CEA"),
                                            html.P("Smt. Ammi Ruhama Toppo, CE CEA"),
                                            html.P("Shri Jitendra Kumar Meena, Director CEA"),
                                            html.P("Shri Anshuman Swain, Deputy Director CEA"),
                                        ],
                                    ),
                                    html.Div(
                                        style={"marginTop": "10px", "fontSize": "16px", "textAlign": "left"},
                                        children=[
                                            html.H4("Developed by: "),
                                            html.P("Dr. Puneet Chitkara (+91 9811611522)"),
                                            html.P("Ashish Chopra (+91 7060334483)"),
                                            html.P("Ashutosh Pande (+91 9650629106)"),
                                            html.P("Adamya Sharma (+91 9987183305)"),
                                        ],
                                    ),
                                    ],
                                    style={"display": "flex", "justifyContent": "center",
                                           "gap": "20px",
                                    }
                                ),
                                html.P(
                                    "This work is inspired by the research of Professor Benjamin F. Hobbs and his team at Johns Hopkins University, where Dr. Chitkara was a postdoctoral researcher. The contributions of Professor Hobbs to stochastic expansion planning and resource adequacy have provided a strong foundation for this model. ",
                                    style={
                                        "marginTop": "20px",
                                        "fontSize": "16px",
                                        "maxWidth": "800px",
                                        "marginLeft": "auto",
                                        "marginRight": "auto",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "width": "80vw",
                        "display": "flex",
                        "flex-direction": "column",
                        "alignItems": "center",
                    },
                    children=[
                        html.H3("User Manual", style={"marginTop": "30px"}),
                        html.Button(
                                    "Download",
                                    id="download-manual-button",
                                    n_clicks=0,
                                    style={
                                        "width": "11vw",
                                        "border": "none",
                                        "border-radius": "10px",
                                        "minHeight": "35px",
                                        "maxHeight": "35px",
                                        "fontWeight": 700,
                                        "padding": "5px",
                                        "color": "#FFFFFF",
                                        "background": "#134A94",
                                    },
                                ),
                        html.Iframe(
                            src="/assets/Stellar SOP.pdf#toolbar=0&navpanes=0&scrollbar=0",
                            style={
                                "width": "70%",
                                "height": "600px",
                                "border": "none",
                                "marginTop": "20px",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)

def register_callbacks(app):
    @app.callback(
        Output("download-pdf", "data"),
        Input("download-manual-button", "n_clicks"),
        prevent_initial_call=True
)
    def download_pdf(n_clicks):

        pdf_path = get_resource_path('assets/Stellar SOP.pdf')
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            return None
        
        return dcc.send_file(
            pdf_path, 
            filename='Stellar_SOP.pdf'
        )