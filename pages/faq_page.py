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
            dcc.Link(
                html.Div(
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "width": "10vw",
                        "position": "absolute",
                        "bottom": "27vh",
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
                    "bottom": "20vh",
                },
                children=[
                    html.Img(
                        src="assets/faq_blue_icon.png",
                        style={
                            "height": "3vh",
                            "width": "1.5vw",
                        },
                    ),
                    html.Button(
                        "FAQ",
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
    """Get absolute path to resource, works for dev and for PyInstaller"""
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
        dcc.Download(id="download-ppt"),
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
                        "width": "80vw",
                        "display": "flex",
                        "flex-direction": "column",
                        "alignItems": "center",
                    },
                    children=[
                        html.H3("FAQ", style={"marginTop": "30px"}),
                        html.Iframe(
                            src="/assets/Stellar FAQs.pdf#toolbar=0&navpanes=0&scrollbar=0",
                            style={
                                "width": "70%",
                                "height": "600px",
                                "border": "none",
                                "marginTop": "20px",
                            },
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "width": "80vw",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                    },
                    children=[
                        html.H3("PPT", style={"marginTop": "30px"}),
                        html.Button(
                            "Download Stellar Presentation",
                            id="download-ppt-button",
                            style={
                                "marginTop": "20px",
                                "fontSize": "16px",
                                "background": "#134A94",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "10px",
                                "padding": "10px 15px",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)


def register_callbacks(app):
    # Existing callbacks...

    @app.callback(
        Output("download-ppt", "data"),
        Input("download-ppt-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_ppt(n_clicks):
        ppt_path = get_resource_path("assets/Stellar.pptx")
        if not os.path.exists(ppt_path):
            print(f"Error: PPT file not found at {ppt_path}")
            return None

        return dcc.send_file(ppt_path, filename="Stellar_Presentation.ppt")
 