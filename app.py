import dash
from dash import dcc, html, State, no_update
from dash.dependencies import Input, Output
import webbrowser
from threading import Timer
# Add the absolute path to your `pages` directory
import os
# from pages import home_page, input_dashboard, login_page, output_dashboard_copy, choose_approach, run_model_dashboard, help_page, faq_page, rep_days_dashboard, Copula_Dash, view_customers, view_load_shift, view_optimised_tariff
# from pages import home_page, input_dashboard, login_page, output_dashboard_copy, choose_approach, run_model_dashboard, help_page, faq_page, rep_days_dashboard, Copula_Dash, view_customers, view_load_shift, view_optimised_tariff


from pages import login_page , choose_approach, run_individual_model , run_cluster_model,   view_load_shift, view_optimised_tariff , compare_results_individual, compare_results_cluster , view_load_shift_cluster
import json
import plotly.graph_objects as go
import pandas as pd

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
    ]
)
app.scripts.append_script({"external_url": "https://cdn.plot.ly/plotly-latest.min.js"})
server = app.server

app.layout = html.Div([
    dcc.Interval(id="run-model-loading-interval", interval=1000, n_intervals=0),
    dcc.Store(id='run-model-loading-state-store', data={'is_loading': False}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

login_page.register_callbacks(app)
choose_approach.register_callbacks(app)
#output_dashboard_copy.register_callbacks(app)
#run_model_dashboard.register_callbacks(app)
#input_dashboard.register_callbacks(app)
#new_copula.register_callbacks(app)
run_individual_model.register_callbacks(app)
run_cluster_model.register_callbacks(app)
# rep_days_dashboard.register_callbacks(app)
# Copula_Dash.register_callbacks(app)
#view_customers.register_callbacks(app)
view_load_shift.register_callbacks(app)
compare_results_individual.register_callbacks(app)
view_load_shift_cluster.register_callbacks(app)
compare_results_cluster.register_callbacks(app)

#view_optimised_tariff.register_callbacks(app)
# help_page.register_callbacks(app)
# faq_page.register_callbacks(app)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    #Input("copula-status-store", "data")
)
def display_page(pathname):
    #if pathname == '/login':
    #    return login_page.layout , print("Redirecting to:", pathname)
    #elif pathname == '/run-model':
    #    return run_model_dashboard.layout
    #elif pathname == '/choose-approach':
    #if pathname == '/choose-approach':
    #    return choose_approach.layout
    if pathname == '/run-individual-model':
        return run_individual_model.layout
    #    return run_model_dashboard.layout
    elif pathname == '/run-cluster-model':
        return run_cluster_model.layout
        #return run_individual_model.layout
    #elif pathname == '/output-dashboard':
    #    return output_dashboard_copy.layout
    # elif pathname == "/tou-graphs":
    #     return view_customers.view_customer_layout
    elif pathname == "/load-graphs":
        return view_load_shift.layout
    elif pathname == "/compare-results":
        return compare_results_individual.layout
    elif pathname == "/load-cluster-graphs":
        return view_load_shift_cluster.layout
    elif pathname == "/compare-cluster-results":
        return compare_results_cluster.layout
    #elif pathname == '/input-dashboard':
    #    return input_dashboard.layout
    #elif pathname == '/help':
    #    return help_page.layout
    #elif pathname == '/faq':
    #    return faq_page.layout
    else:
        #return home_page.layout
        #return run_cluster_model.layout   
        return choose_approach.layout
        #return compare_results_cluster.layout


@app.callback(
    [Output("loading-animation-run-model", "style"),
    Output("loading-animation-run-model-modal", "style"),
     Output("stellar-running-notification", "style")],
    [Input('run-model-loading-state-store', 'data'),
     Input('url', 'pathname')]
)
def update_loader_and_notification(store_data, pathname):
    # Base style for the loading animation
    base_style = {
        "display": "none",
        "marginLeft": "5px",
        "width": "10px",
        "height": "10px",
        "border": "5px solid #f3f3f3",
        "borderTop": "5px solid #4B5563",
        "borderRadius": "50%",
        "animation": "spin 1s linear infinite"
    }

    # Notification div style - hidden by default
    notification_style = {
        "position": "fixed",
        "top": "10px",
        "left": "50%",
        "transform": "translateX(-50%)",
        "width": "18vw",
        "padding": "12px 18px",
        "backgroundColor": "#E6F0F9",  # Light blue background
        "border": "1px solid #91d5ff",  # Medium blue border
        "borderRadius": "6px",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",  # Enhanced shadow for pop-up effect
        "zIndex": "1050",
        "display": "none",
        "animation": "fadeIn 0.3s ease-in-out",  # Add subtle animation
    }

    if not store_data or not store_data.get('is_loading', False):
        return base_style, base_style, notification_style

    # Update loader style when loading
    base_style.update({
        "display": "inline-block",
    })

    # Show notification when loading
    notification_style.update({
        "display": "block",
    })

    # Customize based on pathname
    if pathname == '/run-model':
        base_style.update({
            "borderTop": "5px solid #134A94",
        })
    modal_style = base_style
    modal_style.update({
            "borderTop": "5px solid #134A94",
        })

    return base_style, modal_style, notification_style


if __name__ == "__main__":
    Timer(1, open_browser).start()
    # app.run(dev_tools_ui=True,use_reloader=False,)
    app.run(debug=True,use_reloader=False)
