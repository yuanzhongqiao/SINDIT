from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from frontend import api_client

from dash import html
import numpy as np

from frontend.left_sidebar.global_information import global_information_layout
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeDeep,
    TimeseriesNodeFlat,
)
from util.environment_and_configuration import ConfigGroups, get_configuration
from util.log import logger
from dateutil import tz

logger.info("Initializing pipeline extension callbacks...")


def _generic_stage_info(status_dict) -> str:
    if status_dict.get("active"):
        return "Currently running..."
    elif status_dict.get("last_run") is not None:
        last_run = datetime.fromisoformat(status_dict.get("last_run")).astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        return f"Last run: {last_run.strftime('%H:%M:%S, %d.%m.%Y')}"
    else:
        return "Not yet processed on this instance."


@app.callback(
    Output("pipeline-info-stage-1-status", "children"),
    Output("pipeline-feature-extraction-button", "disabled"),
    Output("pipeline-info-stage-2-status", "children"),
    Output("pipeline-dimensionality-reduction-button", "disabled"),
    Output("pipeline-info-stage-3-status", "children"),
    Output("pipeline-ts-clustering-button", "disabled"),
    Output("pipeline-info-stage-4-status", "children"),
    Output("pipeline-text-keyphrase-extraction-button", "disabled"),
    Output("pipeline-info-stage-5-status", "children"),
    Output("pipeline-cad-analysis-button", "disabled"),
    Output("pipeline-info-stage-6-status", "children"),
    Output("pipeline-image-analysis-button", "disabled"),
    Output("pipeline-info-stage-7-status", "children"),
    Output("pipeline-asset-similarity-button", "disabled"),
    Input("annotation-information-collapse", "is_open"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=False,
)
def pipeline_info(info_open, _):
    if info_open:
        status_dict = api_client.get_json("/similarity_pipeline/status")
        if status_dict is not None:

            stage1_status_dict = status_dict.get("time_series_feature_extraction")
            stage2_status_dict = status_dict.get("time_series_dimensionality_reduction")
            stage3_status_dict = status_dict.get("time_series_clustering")
            stage4_status_dict = status_dict.get("text_keyphrase_extraction")
            stage5_status_dict = status_dict.get("cad_analysis")
            stage6_status_dict = status_dict.get("image_analysis")
            stage7_status_dict = status_dict.get("asset_similarity")

            stage1_disabled = stage1_status_dict.get("active")
            stage2_disabled = (
                stage1_disabled
                or stage2_status_dict.get("active")
                or stage1_status_dict.get("last_run") is None
            )
            stage3_disabled = (
                stage2_disabled
                or stage3_status_dict.get("active")
                or stage2_status_dict.get("last_run") is None
            )
            stage4_disabled = stage4_status_dict.get("active")
            stage5_disabled = stage5_status_dict.get("active")
            stage6_disabled = stage6_status_dict.get("active")
            stage7_disabled = (
                stage3_disabled
                or stage4_disabled
                or stage5_disabled
                or stage6_disabled
                or stage7_status_dict.get("active")
                or stage3_status_dict.get("last_run") is None
                or stage4_status_dict.get("last_run") is None
                or stage5_status_dict.get("last_run") is None
                or stage6_status_dict.get("last_run") is None
            )

            return (
                _generic_stage_info(stage1_status_dict),
                stage1_disabled,
                _generic_stage_info(stage2_status_dict),
                stage2_disabled,
                _generic_stage_info(stage3_status_dict),
                stage3_disabled,
                _generic_stage_info(stage4_status_dict),
                stage4_disabled,
                _generic_stage_info(stage5_status_dict),
                stage5_disabled,
                _generic_stage_info(stage6_status_dict),
                stage6_disabled,
                _generic_stage_info(stage7_status_dict),
                stage7_disabled,
            )

    return None


@app.callback(
    Output("pipeline-feature-extraction-button-toggled", "data"),
    Input("pipeline-feature-extraction-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_ts_feature_extraction(n):

    api_client.post(
        "/similarity_pipeline/time_series_feature_extraction",
    )

    return None


@app.callback(
    Output("pipeline-dimensionality-reduction-button-toggled", "data"),
    Input("pipeline-dimensionality-reduction-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_ts_dimensionality_reduction(n):

    api_client.post(
        "/similarity_pipeline/time_series_dimensionality_reduction",
    )

    return datetime.now()


@app.callback(
    Output("pipeline-ts-clustering-button-toggled", "data"),
    Input("pipeline-ts-clustering-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_ts_clustering(n):

    api_client.post(
        "/similarity_pipeline/time_series_clustering",
    )

    return None


@app.callback(
    Output("pipeline-text-keyphrase-extraction-button-toggled", "data"),
    Input("pipeline-text-keyphrase-extraction-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_text_keyphrase_extraction(n):

    api_client.post(
        "/similarity_pipeline/text_keyphrase_extraction",
    )

    return None


@app.callback(
    Output("pipeline-cad-analysis-button-toggled", "data"),
    Input("pipeline-cad-analysis-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_cad_analysis(n):

    api_client.post(
        "/similarity_pipeline/cad_analysis",
    )

    return None


@app.callback(
    Output("pipeline-image-analysis-button-toggled", "data"),
    Input("pipeline-image-analysis-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_image_analysis(n):

    api_client.post(
        "/similarity_pipeline/image_analysis",
    )

    return None


@app.callback(
    Output("pipeline-asset-similarity-button-toggled", "data"),
    Input("pipeline-asset-similarity-button", "n_clicks"),
    prevent_initial_call=True,
)
def execute_stage_asset_similarity(n):

    api_client.post(
        "/similarity_pipeline/asset_similarity",
    )

    return None


@app.callback(
    Output("factory-graph-header", "className"),
    Output("factory-graph-header-time-series-plot-alternative", "className"),
    Output("kg-container", "className"),
    Output("pca-scatter-graph", "className"),
    Input("show-pca-plot-toggle", "value"),
    prevent_initial_call=True,
)
def toggle_show_pca_scatter(toggle_value):
    activated = True in toggle_value

    if activated:
        return (
            "main-graph-visibility-switch-hidden",
            "",
            "main-graph-visibility-switch-hidden",
            "",
        )
    else:
        return (
            "",
            "main-graph-visibility-switch-hidden",
            "",
            "main-graph-visibility-switch-hidden",
        )


@app.callback(
    Output("pca-scatter-graph", "figure"),
    Input("pca-scatter-graph", "className"),
    # Input("show-pca-plot-toggle", "value"),
    Input("graph-reload-button", "n_clicks"),
    prevent_initial_call=True,
)
def update_pca_scatter(classname, n):

    ts_json = api_client.get_json("/timeseries/nodes", deep=True)
    # pylint: disable=no-member
    ts_nodes = [TimeseriesNodeDeep.from_json(m) for m in ts_json]

    x = []
    y = []
    z = []
    text = []
    colors = []

    cluster_colors = dict()
    cluster_colors["no_cluster"] = 0
    cluster_color_max = 0

    for ts in ts_nodes:
        if ts.reduced_feature_list is None:
            continue

        x.append(ts.reduced_feature_list[0])
        y.append(ts.reduced_feature_list[1])
        if len(ts.reduced_feature_list) >= 3:
            z.append(ts.reduced_feature_list[2])
        else:
            z.append(0)
        text.append(ts.id_short)
        cluster_id = ts.ts_cluster.iri if ts.ts_cluster is not None else "no_cluster"
        if cluster_colors.get(cluster_id) is None:
            cluster_colors[cluster_id] = cluster_color_max + 1
            cluster_color_max += 1
        colors.append(cluster_colors.get(cluster_id))

    trace = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="markers+text",
        # mode="markers",
        hovertext=text,
        text=text,
        marker=dict(
            size=3,
            # color="#003C65"
            color=colors,  # set color to an array/list of desired values
            # colorscale="Viridis",
            colorscale=[
                "#8c8c8c",
                "#003C65",
                "red",
                "green",
            ],
        ),
    )
    layout = go.Layout(title="Time-series PCA Distribution")
    fig = go.Figure(data=[trace], layout=layout)

    fig.update_traces(showlegend=False, selector=dict(type="scatter3d"))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis_title="First principal component",
            yaxis_title="Second principal component",
            zaxis_title="Third principal component",
        ),
        # paper_bgcolor="LightSteelBlue",
    )

    return fig
