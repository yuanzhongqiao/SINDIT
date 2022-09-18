from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
from dash.exceptions import PreventUpdate
from dash import html
from frontend import api_client
from frontend.app import app
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_extension_callbacks import (
    CreationSteps,
)
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeFlat,
)
from graph_domain.factory_graph_types import NodeTypes
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeFlat
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

sensor_ID = None

TIMESERIES_MAX_DISPLAYED_ENTRIES = get_configuration_float(
    group=ConfigGroups.FRONTEND, key="timeseries_max_displayed_entries"
)


print("Initializing timeseries callbacks...")


@app.callback(
    Output("timeseries-graph-update-interval-passthrough", "children"),
    Input("interval-component", "n_intervals"),
    Input("realtime-switch-input", "value"),
    State("timeseries-graph-update-interval-passthrough", "children"),
)
def timeseries_graph_interval(n, realtime_toggle, pseudo_element_input):
    """Updates a pseudo component whenever the realtime-graph shall be updated.
    Used to avoid unnscessary updates while viewing historic data.

    Args:
        n (_type_): _description_
        realtime_toggle (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not isinstance(pseudo_element_input, int):
        return 0

    if realtime_toggle:
        return pseudo_element_input + 1
    else:
        raise PreventUpdate()


@app.callback(
    Output("timeseries-graph", "figure"),
    Output("timeseries-graph-result-count-info", "children"),
    Output("timeseries-graph-aggregate-info", "children"),
    Input("timeseries-graph-update-interval-passthrough", "children"),
    State("selected-graph-element-store", "data"),
    Input("realtime-switch-input", "value"),
    Input("datetime-selector-date", "value"),
    Input("datetime-selector-time", "value"),
    Input("datetime-selector-range-days", "value"),
    Input("datetime-selector-range-hours", "value"),
    Input("datetime-selector-range-min", "value"),
    Input("datetime-selector-range-sec", "value"),
    Input("annotation-creation-store-step", "data"),
    Input("annotation-creation-date-selector-start", "value"),
    Input("annotation-creation-time-selector-start", "value"),
    Input("annotation-creation-date-selector-end", "value"),
    Input("annotation-creation-time-selector-end", "value"),
    Input("annotation-creation-store-range-start", "data"),
    Input("annotation-creation-store-range-end", "data"),
)
def update_timeseries_graph(
    n,
    selected_el_json,
    realtime_toggle,
    selected_date_str,
    selected_time_str,
    duration_days,
    duration_hours,
    duration_mins,
    duration_secs,
    annotation_creation_step,
    annotation_selected_start_date,
    annotation_selected_start_time,
    annotation_selected_end_date,
    annotation_selected_end_time,
    annotation_selected_range_start_str,
    annotation_selected_range_end_str,
):
    if selected_el_json is None:
        # Cancel if nothing selected
        raise PreventUpdate
    else:
        selected_el: GraphSelectedElement = GraphSelectedElement.from_json(
            selected_el_json
        )

    # If Matcher selected instead of timeseries, retrieve the related timeseries and set mode to annotation_viewer:
    if selected_el.type == NodeTypes.ANNOTATION_TS_MATCHER.value:
        annotation_node_json = api_client.get_str(
            "/annotation/ts_matcher/related_annotation_instance", iri=selected_el.iri
        )
        annotation_node_flat: AnnotationInstanceNodeFlat = (
            AnnotationInstanceNodeFlat.from_json(annotation_node_json)
        )
        # Set annotation_viewer mode:
        annotation_mode_range_selected = True
        annotation_mode_view_defined = True
        annotation_creation_mode_active = False
        annotation_viewer_mode = True
        annotation_selected_range_start_str = None
        annotation_selected_range_end_str = None
        selected_range_start = annotation_node_flat.occurance_start_date_time
        selected_range_end = annotation_node_flat.occurance_end_date_time

        ts_node_json = api_client.get_str(
            "/annotation/ts_matcher/original_annotated_ts", iri=selected_el.iri
        )
        ts_node_flat: TimeseriesNodeFlat = TimeseriesNodeFlat.from_json(ts_node_json)
        # Override selected element with related timeseries
        selected_el = GraphSelectedElement(
            id_short=ts_node_flat.id_short,
            iri=ts_node_flat.iri,
            type=NodeTypes.TIMESERIES_INPUT.value,
            is_node=True,
        )
    else:
        annotation_mode_range_selected = False
        annotation_mode_view_defined = False
        annotation_creation_mode_active = (
            annotation_creation_step is not None
            and annotation_creation_step == CreationSteps.RANGE_SELECTION.value
        )
        annotation_viewer_mode = (
            annotation_creation_step is not None
            and annotation_creation_step > CreationSteps.RANGE_SELECTION.value
        )
    if (
        annotation_creation_mode_active
        and annotation_selected_start_date is not None
        and annotation_selected_start_time is not None
        and annotation_selected_end_date is not None
        and annotation_selected_end_time is not None
    ):
        selector_tz = tz.gettz(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
        annotation_selected_start_datetime = datetime.combine(
            date=datetime.fromisoformat(annotation_selected_start_date).date(),
            time=datetime.fromisoformat(annotation_selected_start_time).time(),
            tzinfo=selector_tz,
        )
        annotation_selected_end_datetime = datetime.combine(
            date=datetime.fromisoformat(annotation_selected_end_date).date(),
            time=datetime.fromisoformat(annotation_selected_end_time).time(),
            tzinfo=selector_tz,
        )
        if (
            annotation_selected_start_datetime < annotation_selected_end_datetime
            and annotation_selected_end_datetime
            < datetime.now().astimezone(
                tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
            )
        ):
            annotation_mode_view_defined = True

            # Alter displayed time-range:
            overridden_duration = (
                annotation_selected_end_datetime - annotation_selected_start_datetime
            )
            overridden_end_datetime = annotation_selected_end_datetime

    if (
        (annotation_creation_mode_active or annotation_viewer_mode)
        and annotation_selected_range_start_str is not None
        and annotation_selected_range_end_str is not None
    ):
        annotation_mode_range_selected = True
        selected_range_start = datetime.fromisoformat(
            annotation_selected_range_start_str
        ).replace(
            tzinfo=tz.gettz(
                get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
            )
        )
        selected_range_end = datetime.fromisoformat(
            annotation_selected_range_end_str
        ).replace(
            tzinfo=tz.gettz(
                get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
            )
        )

    if annotation_viewer_mode:
        # Alter displayed time-range to make the annotation best visible:
        annotation_duration = selected_range_end - selected_range_start
        overridden_end_datetime = selected_range_end + (annotation_duration / 4)
        overridden_duration = annotation_duration * 1.5

    fig = timeseries_graph_layout.get_figure()

    data = pd.DataFrame(columns=["time", "value"])

    # Cancel if anything else than timeseries is selected
    if selected_el.type != NodeTypes.TIMESERIES_INPUT.value:
        print("Trying to visualize timeseries from non-timeseries element...")
        return fig

    if (
        annotation_creation_mode_active and annotation_mode_view_defined
    ) or annotation_viewer_mode:
        duration = overridden_duration
    else:
        duration: timedelta = timedelta(
            days=duration_days,
            hours=duration_hours,
            minutes=duration_mins,
            seconds=duration_secs,
        )

    # API call for the dataframe
    if (
        annotation_creation_mode_active and annotation_mode_view_defined
    ) or annotation_viewer_mode:
        date_time = overridden_end_datetime
    elif realtime_toggle:
        date_time = datetime.now()
    else:
        if isinstance(selected_time_str, str) and selected_time_str != "":
            selected_time = datetime.fromisoformat(selected_time_str).time()
        else:
            selected_time = datetime.now().time()

        if isinstance(selected_date_str, str) and selected_date_str != "":
            selected_date = datetime.fromisoformat(selected_date_str).date()
        else:
            selected_date = datetime.now().date()

        selector_tz = tz.gettz(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
        date_time = datetime.combine(
            date=selected_date,
            time=selected_time,
            tzinfo=selector_tz,
        )

    # API call for the count of readings
    readings_count = int(
        api_client.get_json(
            relative_path="/timeseries/entries_count",
            iri=selected_el.iri,
            duration=duration.total_seconds(),
            date_time_str=date_time.isoformat(),
        )
    )

    # Filtering to avoid loading to large readings datasets
    if readings_count > TIMESERIES_MAX_DISPLAYED_ENTRIES:
        if duration.total_seconds() > timedelta(days=2).total_seconds():
            # More than two days -> use hourly aggregation
            aggregation_window_s = timedelta(hours=1).total_seconds()
        elif duration.total_seconds() > timedelta(hours=6).total_seconds():
            aggregation_window_s = timedelta(minutes=10).total_seconds()
        elif duration.total_seconds() > timedelta(hours=2).total_seconds():
            aggregation_window_s = timedelta(minutes=1).total_seconds()
        elif duration.total_seconds() > timedelta(minutes=10).total_seconds():
            aggregation_window_s = timedelta(seconds=1).total_seconds()
        else:
            aggregation_window_s = timedelta(milliseconds=100).total_seconds()

        aggregation_window_ms = int(aggregation_window_s * 1000)
    else:
        aggregation_window_ms = None

    # API call for the readings
    data = api_client.get_dataframe(
        relative_path="/timeseries/range",
        iri=selected_el.iri,
        duration=duration.total_seconds(),
        date_time_str=date_time.isoformat(),
        aggregation_window_ms=aggregation_window_ms,
    )

    fig.add_trace(
        trace={
            "x": data["time"],
            "y": data["value"],
            "mode": "lines+markers",
            "type": "scatter",
        },
        row=1,
        col=1,
    )

    if (
        annotation_creation_mode_active or annotation_viewer_mode
    ) and annotation_mode_range_selected:

        color_array = []

        i = 0
        for data_point_time in data["time"]:
            if (
                data_point_time >= selected_range_start
                and data_point_time <= selected_range_end
            ):
                # selected_points.append(i)
                color_array.append("#9b5c44")
            else:
                color_array.append("#81a2c4")
            i += 1
    else:
        color_array = ["#446e9b" for data in data["time"]]
    selected_points = [i for i in range(0, len(data["time"]))]
    # Layouting...
    fig.update_traces(
        marker_line=None,
        mode="markers",
        selectedpoints=selected_points,
        opacity=1,
        marker=dict(size=8, color=color_array),
    )

    # Aggregate info
    result_count_str = f"Entries for given range:\t{readings_count}"
    aggregate_info_str = (
        html.Div(
            [
                html.Div("Aggregated view! ", style={"font-weight": "bold"}),
                f"Only showing first readings per {timedelta(milliseconds=aggregation_window_ms)} (h:m:s).",
            ],
            style={"padding-top": "5px"},
        )
        if aggregation_window_ms is not None
        else ""
    )

    if annotation_creation_mode_active:
        # Activate selection mode
        fig.update_layout(
            dragmode="select",
            selectdirection="h",
        )

    return fig, result_count_str, aggregate_info_str
