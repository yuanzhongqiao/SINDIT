from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

from frontend.navbar import navbar_layout
from frontend.right_sidebar import right_sidebar_layout
from frontend.left_sidebar import left_sidebar_layout
from frontend.main_column import main_column_layout
from util.environment_and_configuration import ConfigGroups, get_configuration_int


def get_layout():
    """
    Main page layout
    :return:
    """
    return html.Div(
        style={
            "max-height": "100vh",
            "height": "100vh",
            "display": "flex",
            "flex-direction": "column",
        },
        children=[
            # Navbar:
            navbar_layout.get_layout(),
            # Body:
            dbc.Card(
                style={"flex": 1},
                id="content-card",
                children=[
                    dbc.CardBody(
                        [
                            html.Div(
                                children=[
                                    # Left sidebar (stats):
                                    left_sidebar_layout.get_layout(),
                                    # Main column (graph):
                                    main_column_layout.get_layout(),
                                    # Right sidebar (context details):
                                    right_sidebar_layout.get_layout(),
                                    # Interval pseudo component for periodic refreshes:
                                    dcc.Interval(
                                        id="interval-component",
                                        interval=get_configuration_int(
                                            ConfigGroups.FRONTEND, "refresh_interval"
                                        ),
                                        # interval=cfg.config['frontend']['refresh_interval'],
                                        # interval=5000,
                                        n_intervals=0,
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "flex-flow": "row",
                                    "height": "100%",
                                    "max-height": "100%",
                                    "width": "100%",
                                    "max-width": "100%",
                                },
                                id="content-rows-container",
                            ),
                        ]
                    )
                ],
            ),
        ],
    )
