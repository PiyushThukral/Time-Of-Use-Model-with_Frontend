from dash import html, dcc, Output, Input, callback, ctx
import dash
import dash_bootstrap_components as dbc





layout = html.Div([

    # # Top Left Logo
    # html.Div([
    #     html.Img(src="assets/CEA logo.png", style={
    #         'height': '100px',
    #         'width': '550px',
    #         'position': 'absolute',
    #         'top': '10px',
    #         'left': '10px',
    #     }),
    # ]),

    # Central Content
    html.Div([
        html.Img(src="assets/Stellar Logo.png", style={
            'height': '100px',
            'width': '400px',
            'margin-bottom': '10px',
            'margin-top': '120px',
        }),
        html.H3("Optimized Pricing and Tariff Analysis using Real-time Insights for Fairness and Flexibility", style={
            'color': "#939393",
            'font-weight': 700, 
            'width': '700px',
            'text-align': 'center',
            'margin-top': '10px'
        }),
        html.H4("Choose an approach for Optariff analysis", style={
            'color': "#555",
            'font-weight': '600',
            'font-size': '16px',
            'text-align': 'center',
            'margin-bottom': '30px'
        }),

        # Buttons side-by-side
        html.Div([
            html.Button("Individual Tariff", id="btn-individual", n_clicks=0, style={
                'padding': '12px 24px',
                'fontSize': '13px',
                'border': 'none',
                'border-radius': '6px',
                'color': '#fff',
                'background': '#134A94',
                'width': '240px',
                'margin': '5px'
            }),
            html.Button("Cluster Tariff", id="btn-cluster", n_clicks=0, style={
                'padding': '12px 24px',
                'fontSize': '13px',
                'border': 'none',
                'border-radius': '6px',
                'color': '#fff',
                'background': '#134A94',
                'width': '240px',
                'margin': '5px'
            }),
            dcc.Location(id='redirect', refresh=True)
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'gap': '20px',
            'flexWrap': 'wrap'
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'margin-top': '120px'
    }),

    # User Manual Download Link
    html.Div([
        html.A("📘 Download User Manual", href="/assets/optariff_user_manual.pdf", target="_blank", style={
            'color': '#134A94',
            'font-weight': '600',
            'font-size': '14px',
            'text-decoration': 'underline'
        })
    ], style={
        'position': 'absolute',
        'bottom': '30px',
        'left': '50%',
        'transform': 'translateX(-50%)',
        'text-align': 'center'
    })

], style={
    'backgroundColor': '#E6F0F9',
    'backgroundImage': 'url("/assets/welcome.png")',
    'backgroundSize': 'cover',
    'backgroundRepeat': 'no-repeat',
    'backgroundPosition': 'center',
    'height': '100vh',
    'width': '100vw',
    'margin': 0,
    'padding': 0,
    'overflow': 'hidden',
    'position': 'fixed',
    'top': 0,
    'left': 0
})


# ✅ Register your callbacks here
def register_callbacks(app):
    @app.callback(
        Output("redirect", "href"),
        Input("btn-individual", "n_clicks"),
        Input("btn-cluster", "n_clicks"),
        prevent_initial_call=True
    )
    def redirect_on_click(n1, n2):
        triggered_id = ctx.triggered_id
        if triggered_id == "btn-individual":
            return "/run-individual-model"
        elif triggered_id == "btn-cluster":
            return "/run-cluster-model"
        return dash.no_update
    
