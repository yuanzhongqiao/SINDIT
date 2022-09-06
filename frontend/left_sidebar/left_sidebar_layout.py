import dash_bootstrap_components as dbc
from dash import html

from frontend.left_sidebar.global_information import global_information_layout
from frontend.left_sidebar.visibility_settings import visibility_settings_layout
from frontend.left_sidebar.datetime_selector import datetime_selector_layout


def get_layout():
    """
    Layout of the left sidebar. Contains global information and stats as well as some settings
    :return:
    """
    return html.Div(
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
                    # dbc.AccordionItem(
                    #     [
                    #         html.Div(style={"height": "30px"}),
                    #     ],
                    #     title=""
                    # ),
                    # dbc.AccordionItem(
                    #     [
                    #         global_information_layout.get_layout(),
                    #     ],
                    #     title=""
                    # ),
                    # dbc.AccordionItem(
                    #     [
                    #         html.Div(style={"height": "30px"}),
                    #     ],
                    #     title=""
                    # ),
                    dbc.AccordionItem(
                        [
                            datetime_selector_layout.get_layout(),
                        ],
                        title="Timeseries date-time selection",
                    ),
                ]
            ),
        ],
        style={"flex": "2", "padding": "1rem", "min-width": "250px"},
    )
