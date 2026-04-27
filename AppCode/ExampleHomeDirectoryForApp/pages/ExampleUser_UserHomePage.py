import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__,
                   name = "Home Page: Example User",
                   path="/AddYourOwnHef"
                   )

layout = html.Div(
    [
        html.H2("Home Page: Example User"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Nav(
                    [
                    dbc.NavLink([
                        html.Div(page["name"], className = "ms-2"), 
                        ],
                        href = page["relative_path"], 
                        active = "exact",
                        )
                        for page in dash.page_registry.values()
                        if page["name"].startswith((
                                "Experimental Methods Example", 
                                "P202511 Exemple de rapport"
                                ))
                        ], 
                    vertical = True, 
                    pills = True, 
                    className = "bg-light", 
                    )
                ])
            ]),
        html.Hr(),
        ]
    )