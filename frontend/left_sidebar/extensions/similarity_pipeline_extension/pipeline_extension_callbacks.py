from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output

from frontend import api_client

from dash import html

from frontend.left_sidebar.global_information import global_information_layout
from util.environment_and_configuration import ConfigGroups, get_configuration

print("Initializing pipeline extension callbacks...")
