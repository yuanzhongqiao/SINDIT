from dash import html
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.BaseNode import BaseNode
from frontend import api_client
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from frontend.right_sidebar.node_data_tab.file_visualization import (
    file_visualization_layout,
)
from graph_domain.factory_graph_types import NodeTypes


def get_layout(selected_el: GraphSelectedElement):
    """
    Layout of the node-details tab: e.g. iri, description...
    :param selected_el:
    :return:
    """

    if selected_el is None:
        # No node selected
        return html.Div("Select a node to visualize its details")
    elif selected_el.is_node:
        node_details_json = api_client.get_json("/node_details", iri=selected_el.iri)
        node: BaseNode = BaseNode.from_dict(node_details_json)
        return html.Div(
            children=[
                html.Div("IRI:", className="keyword"),
                html.Div(node.iri),
                html.Div(style={"height": "20px"}),
                html.Div("Description:", className="keyword"),
                html.Div(
                    node.description
                    if node.description is not None and node.description != ""
                    else "No description available"
                ),
            ]
        )
    else:
        # No details for edges
        return html.Div("No details available for edges.")
