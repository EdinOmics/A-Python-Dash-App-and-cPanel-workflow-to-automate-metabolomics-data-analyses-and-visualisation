import dash
from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__,
                   #TODO: Update for each individual user account
                   name = "Home Page: Example User",
                   #TODO: Make sure this matched with the href specified in app.py for this user
                   path="/AddYourOwnAccountHef"
                   )

#TODO: Update for each individual user account
page_title_UserView = "Home Page: Example User" 
#TODO: Update each time you add a new project for this user
# (Should match the page_name specified in that page)
User_ListOfProjects = ("Experimental Methods Example", 
                       "Experimental Results Example")

#TODO: Use replace all to change the suffices of the input and output IDs
# from _ReportsUserName to a unique name for this user's reports

layout = html.Div(
    [
        html.H2(page_title_UserView),
        html.Hr(),

        dcc.Location(id="url_ReportsUserName"),              # fires once on page load
        # html.Div(id="page-content"),         # placeholder
        dbc.Spinner(
            children=[
                html.Div(id="page-content_ReportsUserName"),         # placeholder
                ],
            size = "lg", 
            color = "primary", 
            fullscreen = True
            ),
        ]
    )

def make_nav_from_registry():
    return dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Nav(
                        [
                            dbc.NavLink(
                                [
                                    html.Div(page["name"], className="ms-2"),
                                ],
                                href=page["relative_path"],
                                active="exact",
                            )
                            for page in dash.page_registry.values()
                            if page["name"].startswith((User_ListOfProjects))
                        ],
                        vertical=True,
                        pills=True,
                        className="bg-light",
                    )
                ]
            )
        ]
    )

@callback(
    Output("page-content_ReportsUserName", "children"),
    Input("url_ReportsUserName", "pathname"),               # fires on initial page load
)
def load_page(_pathname):
    # This runs immediately once the page fully loads
    nav = make_nav_from_registry()
    return nav
