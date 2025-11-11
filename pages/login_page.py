from dash import html, dcc, Input, Output, State, no_update
import time

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin"

login_status = "Unauthorised"

layout = html.Div(
    style={
        "display": "flex",
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
        #dcc.Location(id="url", refresh=True),
        html.Div(
            style={
                "flex": 1,
                "display": "flex",
                "flex-direction": "column",
                "align-items": "center",
                "justify-content": "center",
                "position": "relative",
            },
            children=[
                html.Div([
                    html.Img(
                        src="assets/CEA logo.png",
                        style={
                            "height": "60px",
                            "width": "300px",
                            "position": "absolute",
                            "top": "10px",
                            "left": "10px",
                        },
                    ),
                ]),
                html.Img(
                    src="assets/Stellar Logo.png",
                    style={"height": "60px", "width": "240px", "margin-bottom": 0},
                ),
                html.H1("Welcome Back !", style={"margin-bottom": 0}),
                html.P(
                    "Sign in to your account.",
                    style={"color": "#676767", "margin-bottom": "25px"},
                ),
                dcc.Input(
                    id="username",
                    type="text",
                    placeholder="Username",
                    style={
                        "width": "250px",
                        "background-color": "#F1F1F1",
                        "border": "none",
                        "border-radius": "5px",
                        "margin": "10px",
                        "height": "20px",
                        "padding": "5px",
                        "padding-left": "10px",
                    },
                ),
                dcc.Input(
                    id="password",
                    type="password",
                    placeholder="Password",
                    style={
                        "width": "250px",
                        "background-color": "#F1F1F1",
                        "border": "none",
                        "border-radius": "5px",
                        "margin": "10px",
                        "height": "20px",
                        "padding": "5px",
                        "padding-left": "10px",
                    },
                ),
                html.Button(
                    "Login",
                    id="login-button",
                    n_clicks=0,
                    style={
                        "width": "260px",
                        "border": "none",
                        "border-radius": "5px",
                        "margin": "15px",
                        "height": "35px",
                        "padding": "5px",
                        "color": "#FFFFFF",
                        "background": "#134A94",
                    },
                ),
                html.Div(id="login-output", style={"color": "red"}),
            ],
        ),
        html.Div(
            children=[
                html.Div([
                    html.Img(
                        src="assets/Login-Cards.png",
                        style={"width": "400px", "height": "300px"},
                    ),
                ]),
                html.H3(
                    "Use this tool to run your model and effortlessly generate results",
                    style={
                        "width": "500px",
                        "text-align": "center",
                        "margin-top": "20px",
                        "margin-bottom": "10px",
                        "fontSize": "20px",
                    },
                ),
                html.P(
                    "Run your model effortlessly and obtain insights through graphical visualizations and downloadable CSV reports.",
                    style={
                        "width": "500px",
                        "text-align": "center",
                        "color": "#374251",
                        "fontSize": "16px",
                    },
                ),
            ],
            style={
                "flex": 1,
                "background-color": "#E6F0F9",
                "border-radius": "10px",
                "margin": "10px",
                "display": "flex",
                "flex-direction": "column",
                "align-items": "center",
                "justify-content": "center",
            },
        ),
        dcc.Store(id="login-status-store"),
    ],
)


def register_callbacks(app):
    @app.callback(
        Output("login-output", "children"),
        Output("login-output", "style"),
        Output("login-status-store", "data"),
        Output("url", "pathname"),
        Input("login-button", "n_clicks"),
        State("username", "value"),
        State("password", "value"),
        prevent_initial_call=True,
    )
    def handle_login(n_clicks, username, password):
        global login_status
        if not n_clicks:
            return "", {}, None, no_update
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            login_status = "Authorised"
            # redirect to /choose-approach after login success
            return "Login successful! Redirecting...", {"color": "green"}, login_status, "/choose-approach"
        return "Invalid credentials, try again!", {"color": "red"}, None, no_update
