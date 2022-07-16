import base64
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from dash import dcc
from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from graph_domain.SupplementaryFileNode import (
    SupplementaryFileNodeFlat,
    SupplementaryFileTypes,
)
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

print("Initializing file visualization callbacks...")


@app.callback(
    Output("suppl_file_download-notifier", "children"),
    Output("suppl_file_download-notifier", "is_open"),
    Input("suppl_file_download_button", "n_clicks"),
    prevent_initial_call=True,
)
def download_file_notifier(n_clicks):

    return (
        f"Download triggered. This can take a while...",
        True,
    )


@app.callback(
    Output("suppl_file_download", "data"),
    Input("suppl_file_download_button", "n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def download_file(n_clicks, selected_el_json):

    # Cancel if nothing selected
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than a file is selected
    if selected_el.type != NodeTypes.SUPPLEMENTARY_FILE.value:
        print("Trying to download file for non-file element...")
        raise PreventUpdate()

    suppl_file_data = api_client.get_raw(
        relative_path="/supplementary_file/data",
        iri=selected_el.iri,
    )

    suppl_file_details_dict = api_client.get_json(
        relative_path="/supplementary_file/details",
        iri=selected_el.iri,
    )
    suppl_file_details: SupplementaryFileNodeFlat = SupplementaryFileNodeFlat.from_dict(
        suppl_file_details_dict
    )

    return dcc.send_bytes(src=suppl_file_data, filename=suppl_file_details.file_name)


@app.callback(
    Output("suppl_file_visualization_container", "children"),
    Input("suppl_file_visualization_container", "children"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=False,
)
def download_file_notifier(_, selected_el_json):
    """Called only whenenver the container is being loaded to the screen

    Args:
        _ (_type_): _description_
        selected_el_json (_type_): _description_

    Raises:
        PreventUpdate: _description_
        PreventUpdate: _description_

    Returns:
        _type_: _description_
    """

    # Cancel if nothing selected
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than a file is selected
    if selected_el.type != NodeTypes.SUPPLEMENTARY_FILE.value:
        print("Trying to download file for non-file element...")
        raise PreventUpdate()

    # Get type of file
    suppl_file_details_dict = api_client.get_json(
        relative_path="/supplementary_file/details",
        iri=selected_el.iri,
    )
    suppl_file_details: SupplementaryFileNodeFlat = SupplementaryFileNodeFlat.from_dict(
        suppl_file_details_dict
    )

    if suppl_file_details.file_type == SupplementaryFileTypes.IMAGE_JPG.value:

        # Get image
        suppl_file_data = api_client.get_raw(
            relative_path="/supplementary_file/data",
            iri=selected_el.iri,
        )

        # Create figure
        fig = go.Figure()

        # Constants
        img_width = 500
        img_height = 500
        scale_factor = 0.5

        # Add invisible scatter trace.
        # This trace is added to help the autoresize logic work.
        fig.add_trace(
            go.Scatter(
                x=[0, img_width * scale_factor],
                y=[0, img_height * scale_factor],
                mode="markers",
                marker_opacity=0,
            )
        )

        # Configure axes
        fig.update_xaxes(visible=False, range=[0, img_width * scale_factor])

        fig.update_yaxes(
            visible=False,
            range=[0, img_height * scale_factor],
            # the scaleanchor attribute ensures that the aspect ratio stays constant
            scaleanchor="x",
        )

        base64image = base64.b64encode(suppl_file_data).decode("utf-8")

        # Add image
        fig.add_layout_image(
            dict(
                x=0,
                sizex=img_width * scale_factor,
                y=img_height * scale_factor,
                sizey=img_height * scale_factor,
                xref="x",
                yref="y",
                opacity=1.0,
                layer="below",
                source=f"data:image/jpg;base64,{base64image}",
            )
        )

        # Configure other layout
        fig.update_layout(
            width=img_width * scale_factor,
            height=img_height * scale_factor,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
        )

        return dcc.Graph(figure=fig)
    elif suppl_file_details.file_type == SupplementaryFileTypes.CAD_STEP.value:
        # Load file
        suppl_file_data = api_client.get_raw(
            relative_path="/supplementary_file/data",
            iri=selected_el.iri,
        )

    else:

        return datetime.now().isoformat()
