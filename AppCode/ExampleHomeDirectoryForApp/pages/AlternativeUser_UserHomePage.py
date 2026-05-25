import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__,
                   name = "Home Page: Alternative Example User",
                   path="/AddYourOwnAlternativeAccountHef"
                   )

# total_no_pages = 0
# for page in dash.page_registry.values():
#     print(page["module"])
#     print(page["name"])
#     print(page["path"])
#     print(page["relative_path"])
#     print(total_no_pages)
#     total_no_pages += 1
#     print("---------")
# #     # print(page)
# print("total_no_pages in app.py:", total_no_pages)

layout = html.Div(
    [
        html.H3("Home Page: Alternative Example User"),
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
                        #active = True,
                        )
                        for page in dash.page_registry.values()
                        if page["name"].startswith(("User Uploads Data Results Example"))
                        ], 
                    vertical = True, 
                    pills = True, 
                    className = "bg-light", 
                    )
                ])
            ]),
        html.Hr(),
        # html.Div(id="page-1-content_2"),
        ]
    )