import dash_bootstrap_components as dbc
from dash import html

from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement


def get_layout():
    """
    Layout of the graph selector.
    Contains both the intermediate selector storage storing information about the selected node OR edge,
    as well as the graphical output.
    :return:
    """
    return html.Div(
        id="graph-selector-info-container",
        children=[
            dbc.Table(
                [
                    html.Tr(
                        [
                            html.Td("Label:", className="key-td"),
                            html.Td(
                                id="selected-element-label",
                                children=[],
                                className="content-td",
                            ),
                        ],
                        id="selected-element-label-container",
                    ),
                    html.Tr(
                        [
                            html.Td("Short ID:", className="key-td"),
                            html.Td(
                                id="selected-element-id-short",
                                children=[],
                                className="content-td",
                            ),
                        ],
                        id="selected-element-id-short-container",
                    ),
                    html.Tr(
                        [
                            html.Td("Type:", className="key-td"),
                            html.Td(
                                id="selected-element-type",
                                children=[],
                                className="content-td",
                            ),
                        ]
                    ),
                ]
            ),
        ],
    )
