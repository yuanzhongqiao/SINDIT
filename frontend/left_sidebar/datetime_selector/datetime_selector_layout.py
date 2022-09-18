from dash import html, dcc
from datetime import datetime, date, timedelta
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_daq as daq


def get_layout():
    return html.Div(
        id="datetime-selector-container",
        children=[
            html.Div(
                "Range to be displayed:",
                style={"font-weight": "bold", "margin-bottom": "5px"},
            ),
            dbc.Row(
                children=[
                    daq.NumericInput(
                        id="datetime-selector-range-days",
                        className="datetime-selector-input",
                        label="Days",
                        min=0,
                        max=365,
                        value=0,
                        persistence=True,
                        persistence_type="session",
                    ),
                    daq.NumericInput(
                        id="datetime-selector-range-hours",
                        className="datetime-selector-input",
                        label="Hours",
                        min=0,
                        max=24,
                        value=0,
                        persistence=True,
                        persistence_type="session",
                    ),
                    daq.NumericInput(
                        id="datetime-selector-range-min",
                        className="datetime-selector-input",
                        label="Min.",
                        min=0,
                        max=60,
                        value=0,
                        persistence=True,
                        persistence_type="session",
                    ),
                    daq.NumericInput(
                        id="datetime-selector-range-sec",
                        className="datetime-selector-input",
                        label="Sec.",
                        value=10.00,
                        min=0,
                        max=60,
                        persistence=True,
                        persistence_type="session",
                    ),
                ]
            ),
            html.Div(
                "Historic or current data:",
                style={
                    "font-weight": "bold",
                    "margin-bottom": "5px",
                    "margin-top": "20px",
                },
            ),
            dbc.Checklist(
                id="realtime-switch-input",
                options=[{"label": "Show real-time data", "value": True}],
                value=[True],
                persistence=True,
                switch=True,
                persistence_type="session",
            ),
            html.Div(
                "Historic date and time:",
                style={
                    # "font-weight": "bold",
                    "margin-bottom": "5px",
                    # "margin-top": "20px",
                },
            ),
            dmc.DatePicker(
                id="datetime-selector-date",
                # label="Historic date",
                # description="Data visualized up to this date",
                # value=datetime.now().date(),
                # style={"width": 250},
                # required=True,
                disabled=True,
                persistence=True,
                persistence_type="session",
                style={"margin-bottom": "5px"},
            ),
            dmc.TimeInput(
                id="datetime-selector-time",
                # label="Historic time:",
                # description="Data visualized up to this time",
                # style={"width": 250},
                # error="Enter a valid time",
                withSeconds=True,
                # value=datetime.now(),
                persistence=True,
                persistence_type="session",
                disabled=True,
                # style={"color": "currentColor"},
            ),
        ],
    )


def get_content():
    return html.Div("Will contain connection status etc...")
    # TODO: connection status, time, node count, edge count...
    # Directly load from the API as this will be reloaded frequently
