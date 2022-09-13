import dash_bootstrap_components as dbc
from dash import html, dcc

from frontend.left_sidebar.global_information import global_information_layout
from frontend.left_sidebar.visibility_settings import visibility_settings_layout
from frontend.left_sidebar.datetime_selector import datetime_selector_layout
from frontend.left_sidebar.extensions.annotation_detection_extension import (
    annotation_extension_layout,
)
from frontend.left_sidebar.extensions.similarity_pipeline_extension import (
    pipeline_extension_layout,
)


def get_layout():
    """
    Layout of the left sidebar. Contains global information and stats as well as some settings
    :return:
    """
    return html.Div(
        id="left-sidebar-container",
        children=[
            # Storage for accessing the selected element
            dcc.Store(id="left-sidebar-collapsable-store", storage_type="session"),
            html.Div(
                id="left-side-extension-buttons-container",
                children=[
                    dbc.Button(
                        [
                            html.Div(
                                id="similarity-pipeline-button-icon",
                                className="vertical-button-left-collapse-icon",
                            ),
                            html.Div(
                                "Similarity Pipeline",
                                className="vertical-button-left-text",
                            ),
                        ],
                        id="similarity-pipeline-collapse-button",
                        color="primary",
                        size="sm",
                        class_name=["vertical-button-left", "tertiary-color"],
                    ),
                    dbc.Button(
                        [
                            html.Div(
                                id="annotation-detection-button-icon",
                                className="vertical-button-left-collapse-icon",
                            ),
                            html.Div(
                                "Annotation Detection",
                                className="vertical-button-left-text",
                            ),
                        ],
                        id="annotation-detection-collapse-button",
                        color="primary",
                        size="sm",
                        class_name=["vertical-button-left", "quaternary-color"],
                    ),
                ],
            ),
            html.Div(
                id="left-sidebar-main-elements-container",
                children=[
                    html.Div(
                        id="left-sidebar-collapse-similarity-pipeline",
                        className="collapsable-horizontal collapsed-horizontal",
                        children=[
                            html.Div(
                                id="left-sidebar-collapse-similarity-pipeline-content",
                                children=[pipeline_extension_layout.get_layout()],
                            )
                        ],
                    ),
                    html.Div(
                        id="left-sidebar-collapse-annotations",
                        className="collapsable-horizontal collapsed-horizontal",
                        children=[
                            html.Div(
                                id="left-sidebar-collapse-annotations-content",
                                children=[annotation_extension_layout.get_layout()],
                            )
                        ],
                    ),
                    html.Div(
                        id="left-sidebar-collapse-main",
                        className="collapsable-horizontal",
                        children=[
                            html.Div(
                                id="left-sidebar-collapse-main-content",
                                children=[
                                    global_information_layout.get_layout(),
                                    dbc.Accordion(
                                        [
                                            dbc.AccordionItem(
                                                [
                                                    visibility_settings_layout.get_layout(),
                                                ],
                                                title="Graph visibility settings",
                                            ),
                                            dbc.AccordionItem(
                                                [
                                                    datetime_selector_layout.get_layout(),
                                                ],
                                                title="Time-series range selection",
                                            ),
                                        ],
                                        persistence=True,
                                        persistence_type="session",
                                        id="left-sidebar-accordion",
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
