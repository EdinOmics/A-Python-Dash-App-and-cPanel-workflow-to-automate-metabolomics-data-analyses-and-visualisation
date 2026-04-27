"""
 CREDIT: This code is adapted for `pages`  based on Nader Elshehabi's  article:
   https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2
   https://github.com/naderelshehabi/dash-flask-login

For other Authentication options see:
  Dash Enterprise:  https://dash.plotly.com/authentication#dash-enterprise-auth
  Dash Basic Auth:  https://dash.plotly.com/authentication#basic-auth

"""


from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, current_user
import dash_bootstrap_components as dbc
import json

import dash
from dash import dcc, html, Input, Output, State

import warnings
from pandas.errors import SettingWithCopyWarning
#Suppress certain common warning messages that do not impact app performance (clog up terminal/error log output)
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)
app = dash.Dash(
    __name__, server=server, 
    use_pages=True, 
    suppress_callback_exceptions=True, 
    external_stylesheets = [dbc.themes.CERULEAN],
)

#Load Username and Password details
# reading the data from the file 
with open('AccessDetails.txt') as f: 
    data = f.read() 
# reconstructing the data as a dictionary 
VALID_USERNAME_PASSWORD = json.loads(data) 


# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
# server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
server.config.update(SECRET_KEY="add_your_own_secret_key")

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"

class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)


app.layout = html.Div(
    [
     dbc.Container([
         dbc.Row([
             dbc.Col([
                 html.Img(src = "assets/university-of-edinburgh-logo.png", 
                          height = "120px"
                          )
                 ],
                 xs = {"size":5, "offset":1}, 
                 md = {"size":1, "offset":0}, 
                 lg = {"size":1, "offset":0},
                 xl = {"size":1, "offset":0}
                 ),
             dbc.Col([
                 html.Img(src = "assets/EdinOmics_Logo_transparent.png", 
                          height = "120px"
                          )
                 ],
                 xs = {"size":5, "offset":1}, 
                 md = {"size":1, "offset":1}, 
                 lg = {"size":1, "offset":1},
                 xl = {"size":1, "offset":1}
                 ),
             dbc.Col([
             	html.H1('EdinOmics Metabolomics Reports', 
                      style={'textAlign': 'center'}),
                 ], 
                 xs = {"size":12, "offset":0}, 
                 md = {"size":9, "offset":0}, 
                 lg = {"size":9, "offset":0},
                 xl = {"size":9, "offset":0}
                 )
             ], align = "center"),
         dcc.Location(id="url"),
         html.Hr(),
         html.Div(id="user-status-header"),
         html.Hr(),
         dash.page_container,
         html.Br(),
         html.Hr(),
         html.Footer("""Use the following standard text to acknowledge the omics work performed at EdinOmics: "The metabolomics analyses were carried out by the EdinOmics research facility (RRID: SCR_021838) at the University of Edinburgh". Please do not forget to acknowledge the facility in your scientific publications, if you include data generated with us.""", 
                     style={'textAlign': 'center'}
                     ),
         html.Br(),
         html.Footer("Please communicate with and acknowledge specific facility staff if they were involved in performing experiments or provided more involved training/advice/work for you. Please make sure you consider co-authorship if their contributions go beyond this.", 
                     style={'textAlign': 'center'}
                     ),
         html.Br(),
         html.Footer("We offer a complimentary manuscript review service. We encourage to use it for your thesis or article.", 
                     style={'textAlign': 'center'}
                     ),
         html.Br(), 
         html.Footer("Interactive dashboard developed by Jessica M. O'Loughlin.", 
                     style={'textAlign': 'center'}
                     ),
         html.Br(),
         html.Center(
             html.A('EdinOmics Facility, The University of Edinburgh', 
                    href='https://www.ed.ac.uk/biology/research/facilities/edinomics'),
             ),
         html.Br(),
         ]),
     ]
    )

@app.callback(
    Output("user-status-header", "children"),
    Input("url", "pathname"),
)
def update_authentication_status(_):
    if current_user.is_authenticated:
        return dcc.Link("Logout", href="/logout")#, dash.page_container
    return dcc.Link("Login", href="/")


@app.callback(
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"), 
    )
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:
        if VALID_USERNAME_PASSWORD.get(username) is None:
            return "Invalid Username or Password"
        #If correct login details provided: direct the user to their own home page to access their project pages
        # Add in addional users as 'elif' arguments
        if VALID_USERNAME_PASSWORD.get(username) == password:
            login_user(User(username))
            if current_user.get_id() == "ExampleUsername":
                children = ["Login Successful ", dcc.Link("View Reports", href="/AddYourOwnHef")] 
            elif current_user.get_id() == "AlternativeExampleUsername": #Just put in as an example of how to add more user accounts
                children = ["Login Successful ", dcc.Link("View Reports", href="/AddYourOwnAlternativeHef")]
            else:
                children = "Incorrect Username or Password. Is issue persists, contact EdinOmics for assistance."

            return children
        children = "Incorrect Username or Password. Is issue persists, contact EdinOmics for assistance"
        return children
    
    
if __name__ == "__main__":
    app.run(debug=True)

