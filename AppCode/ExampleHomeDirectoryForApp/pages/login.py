import dash
from dash import html, dcc

dash.register_page(__name__, path="/")

# Login screen
layout = html.Div(
    [
        html.H3("Log in to continue:", id="h1"),
        html.P("Enter your username and password to access your data and files generated with EdinOmics. If you have forgotten this, please contact us via edinomic@ed.ac.uk."),
        dcc.Input(placeholder="Enter your username", type="text", id="uname-box"),
        dcc.Input(placeholder="Enter your password", type="password", id="pwd-box"),
        html.Button(children="Login", n_clicks=0, type="submit", id="login-button"),
        html.Div(children="", id="output-state"),
        # html.Br(),
        # dcc.Link("Home", href="/"),
    ]
)

