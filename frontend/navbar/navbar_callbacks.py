from dash.dependencies import Input, Output, State
from dash import dcc
from frontend.app import app
from frontend import api_client

print("Initializing navbar callbacks...")


@app.callback(
    Output("help-offcanvas", "is_open"),
    Input("help-button", "n_clicks"),
    [State("help-offcanvas", "is_open")],
    prevent_initial_call=True,
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("import-export-dropdown", "is_open"),
    Output("exportable-databases-dropdown", "options"),
    Input("import-export-button", "n_clicks"),
    State("import-export-dropdown", "is_open"),
    prevent_initial_call=True,
)
def toggle_popover(n, is_open):
    exportable_dbs = []
    if not is_open:
        # Load content
        options = api_client.get_json("/export/database_list")

        exportable_dbs = [
            {"value": option[0], "label": option[1]} for option in options
        ]

    return not is_open, exportable_dbs


@app.callback(
    Output("export-single-button", "disabled"),
    Input("exportable-databases-dropdown", "value"),
    prevent_initial_call=True,
)
def download_single_button_active(selected):
    if selected is not None:
        return False
    return True


@app.callback(
    Output("export-started-notifier", "is_open"),
    Input("export-all-button", "n_clicks"),
    Input("export-single-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_single_notifier(n, m):
    # Separate callback to display the notifier before the end of the main callback!
    return True


@app.callback(
    Output("export-single-download", "data"),
    Input("export-single-button", "n_clicks"),
    State("exportable-databases-dropdown", "value"),
    prevent_initial_call=True,
)
def download_single(n, selected_db):
    print(f"Startet export for single database: {selected_db}")

    file_data = api_client.get_raw(
        relative_path="/export/database_dump",
        database_iri=selected_db,
        all_databases=False,
    )

    # suppl_file_details_dict = api_client.get_json(
    #     relative_path="/supplementary_file/details",
    #     iri=selected_el.iri,
    # )
    # suppl_file_details: SupplementaryFileNodeFlat = SupplementaryFileNodeFlat.from_dict(
    #     suppl_file_details_dict
    # )

    return dcc.send_bytes(src=file_data, filename="test-file.txt")


@app.callback(
    Output("export-all-download", "data"),
    Input("export-all-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_all(n):
    print("Startet export for all databases")


# @app.callback(
#     Output("output-data-upload", "children"),
#     Input("upload-data", "contents"),
#     State("upload-data", "filename"),
#     State("upload-data", "last_modified"),
#     prevent_initial_call=True,
# )
# def upload_file(list_of_contents, list_of_names, list_of_dates):
#     pass
# if list_of_contents is not None:
#     children = [
#         parse_contents(c, n, d)
#         for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
#     ]
#     return children
