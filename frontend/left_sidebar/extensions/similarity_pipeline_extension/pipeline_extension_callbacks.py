from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output

from frontend import api_client

from dash import html

from frontend.left_sidebar.global_information import global_information_layout
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

    return None


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
