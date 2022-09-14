from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

from frontend.navbar import navbar_layout
from frontend.right_sidebar import right_sidebar_layout
from frontend.left_sidebar import left_sidebar_layout
from frontend.main_column import main_column_layout
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_int,
)


def get_layout():
    """
    Main page layout
    :return:
    """
    return html.Div(
        id="full-page-container",
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
                                        n_intervals=0,
                                    ),
                                    dcc.Interval(
                                        id="interval-component-factory-graph",
                                        interval=get_configuration_int(
                                            ConfigGroups.FRONTEND,
                                            "refresh_interval_factory_graph",
                                        ),
                                        n_intervals=0,
                                    ),
                                    dcc.Interval(
                                        id="interval-component-factory-graph-initial-loading",
                                        interval=2000,
                                        n_intervals=0,
                                        max_intervals=4,
                                    ),
                                ],
                                id="content-rows-container",
                            ),
                            html.Div(
                                id="publication-info-container",
                                children=[
                                    html.Div(
                                        id="publication-date-container",
                                        className="publication-info-subcontainer",
                                        children=[
                                            html.Div(
                                                "Publication date:",
                                                className="publication-info-key",
                                            ),
                                            html.Div(
                                                get_configuration(
                                                    group=ConfigGroups.GENERIC,
                                                    key="publication_date",
                                                )
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="license-container",
                                        className="publication-info-subcontainer",
                                        children=[
                                            html.Div(
                                                "License:",
                                                className="publication-info-key",
                                            ),
                                            html.Div(
                                                id="license-text-container",
                                                children=[
                                                    # "This work and the data is restricted by the ",
                                                    html.A(
                                                        "Creative Commons Attribition Non Commercial Share Alike 4.0 International license",
                                                        href="https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode",
                                                    ),
                                                    # ".",
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="github-link-container",
                                        className="publication-info-subcontainer",
                                        children=[
                                            html.Div(
                                                "Source code:",
                                                className="publication-info-key",
                                            ),
                                            html.A(
                                                "https://github.com/SINTEF-9012/SINDIT",
                                                href="https://github.com/SINTEF-9012/SINDIT",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        id="main-card-body",
                    )
                ],
            ),
        ],
    )
