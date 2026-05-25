import os
import sys

from app import app as dash_app

dash_app.scripts.config.serve_locally = True

application = dash_app.server