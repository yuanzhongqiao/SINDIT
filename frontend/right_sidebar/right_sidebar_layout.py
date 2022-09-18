import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from frontend.right_sidebar.graph_selector_info import graph_selector_info_layout


def get_layout():
    """
    Layout of the right sidebar. Contains context details for selected elements of the main graph
    :return:
    """
    return html.Div(
        id="right-sidebar-collapse",
        className="sidebar-collapsed",
        children=[
            dbc.Card(
                id="right-sidebar-card",
                children=[
                    dbc.CardHeader(
                        id="right-sidebar-card-header",
                        children=[html.Div("Selected element")],
                    ),
                    dbc.CardBody(
                        id="right-sidebar-card-body",
                        children=[
                            # Selected node / edge:
                            graph_selector_info_layout.get_layout(),
                            # Tabs:
                            dbc.Tabs(
                                id="tabs-infos",
                                active_tab="tab-node-data",
                                children=[],
                                persistence=True,
                                persistence_type="session",
                            ),
                            html.Div(id="tabs-content"),
                            dcc.Store(
                                id="last-manually-selected-tab",
                                storage_type="session",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
