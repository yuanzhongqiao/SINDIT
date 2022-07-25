import base64
from datetime import datetime, timedelta
import io
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
from dash_vtk.utils import to_mesh_state
import plotly.graph_objects as go
from stl import mesh  # pip install numpy-stl
import plotly.graph_objects as go
import numpy as np
import cadquery
import cqkit

# import OCC
# from OCC.STEPControl import STEPControl_Reader
# from OCC.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
# from OCC.Visualization import Tesselator, atNormal

# from cadquery import exporters
import dash_vtk

# import cadquery as cq
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


def stl2mesh3d(stl_mesh):
    # stl_mesh is read by nympy-stl from a stl file; it is  an array of faces/triangles (i.e. three 3d points)
    # this function extracts the unique vertices and the lists I, J, K to define a Plotly mesh3d
    p, q, r = stl_mesh.vectors.shape  # (p, 3, 3)
    # the array stl_mesh.vectors.reshape(p*q, r) can contain multiple copies of the same vertex;
    # extract unique vertices from all mesh triangles
    vertices, ixr = np.unique(
        stl_mesh.vectors.reshape(p * q, r), return_inverse=True, axis=0
    )
    I = np.take(ixr, [3 * k for k in range(p)])
    J = np.take(ixr, [3 * k + 1 for k in range(p)])
    K = np.take(ixr, [3 * k + 2 for k in range(p)])
    return vertices, I, J, K


@app.callback(
    Output("suppl_file_visualization_container", "children"),
    Input("suppl_file_visualization_container", "children"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=False,
)
def visualize_file(_, selected_el_json):
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

        # step_import = cadquery.importers.importStep(
        #     "./learning_factory_instance/binaries_import/hbw.step"
        # )

        # cadquery.exporters.export(step_import, "hbw_export.stl", tolerance=1000000000)

        # my_mesh = mesh.Mesh.from_file("hbw_export.stl")

        # step_import = cqkit.importers.importStep(
        #     "./learning_factory_instance/binaries_import/hbw.step"
        # )

        # cqkit.export_stl_file(step_import, "hbw_export2.stl", tolerance=1000000000)

        cad_data = api_client.get_raw(
            relative_path="/supplementary_file/data",
            iri=selected_el.iri + "_stl_conversion",
        )

        cad_file_handle = io.BytesIO(cad_data)

        cad_mesh = mesh.Mesh.from_file(
            filename="cad", fh=cad_file_handle  # Filename not used
        )
        # step_import = import_step_from_handle(cad_file_handle)

        # tmp_file_name = ".tmp/cad_export_" + datetime.now().isoformat() + ".stl"

        # # Does not seem to be easily achievelable without writing to a file with the given libraries
        # cqkit.export_stl_file(step_import, ".tmp/", tolerance=1000000000)

        # my_mesh = mesh.Mesh.from_file(tmp_file_name)

        # my_mesh = mesh.Mesh.from_file("test2.stl")
        # stl file from: https://github.com/stephenyeargin/stl-files/blob/master/AT%26T%20Building.stl
        cad_mesh.vectors.shape

        # (2267, 3, 3)

        vertices, I, J, K = stl2mesh3d(cad_mesh)
        x, y, z = vertices.T

        vertices.shape

        # (1171, 3)

        colorscale = [[0, "#e5dee5"], [1, "#e5dee5"]]

        mesh3D = go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=I,
            j=J,
            k=K,
            flatshading=True,
            colorscale=colorscale,
            intensity=z,
            name="AT&T",
            showscale=False,
        )

        layout = go.Layout(
            paper_bgcolor="rgb(1,1,1)",
            font_color="white",
            # width=250,
            # height=250,
            scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
            scene_xaxis_visible=False,
            scene_yaxis_visible=False,
            scene_zaxis_visible=False,
        )

        fig = go.Figure(data=[mesh3D], layout=layout)

        fig.data[0].update(
            lighting=dict(
                ambient=0.18,
                diffuse=1,
                fresnel=0.1,
                specular=1,
                roughness=0.1,
                facenormalsepsilon=0,
            )
        )
        fig.data[0].update(lightposition=dict(x=3000, y=3000, z=10000))

        return dcc.Graph(figure=fig)

        #
        #
        #
        #
        #
        #
        #
        #

        step_import = cadquery.importers.importStep(
            "./learning_factory_instance/binaries_import/hbw.step"
        )

        cadquery.exporters.export(step_import, "hbw_export.stl", tolerance=1000000000)

        my_mesh = mesh.Mesh.from_file("hbw_export.stl")

        step_import = cqkit.importers.importStep(
            "./learning_factory_instance/binaries_import/hbw.step"
        )

        cqkit.export_stl_file(step_import, "hbw_export2.stl", tolerance=1000000000)

        my_mesh = mesh.Mesh.from_file("hbw_export2.stl")

        # my_mesh = mesh.Mesh.from_file("test2.stl")
        # stl file from: https://github.com/stephenyeargin/stl-files/blob/master/AT%26T%20Building.stl
        my_mesh.vectors.shape

        # (2267, 3, 3)

        vertices, I, J, K = stl2mesh3d(my_mesh)
        x, y, z = vertices.T

        vertices.shape

        # (1171, 3)

        colorscale = [[0, "#e5dee5"], [1, "#e5dee5"]]

        mesh3D = go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=I,
            j=J,
            k=K,
            flatshading=True,
            colorscale=colorscale,
            intensity=z,
            name="AT&T",
            showscale=False,
        )

        layout = go.Layout(
            paper_bgcolor="rgb(1,1,1)",
            font_color="white",
            # width=250,
            # height=250,
            scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
            scene_xaxis_visible=False,
            scene_yaxis_visible=False,
            scene_zaxis_visible=False,
        )

        fig = go.Figure(data=[mesh3D], layout=layout)

        fig.data[0].update(
            lighting=dict(
                ambient=0.18,
                diffuse=1,
                fresnel=0.1,
                specular=1,
                roughness=0.1,
                facenormalsepsilon=0,
            )
        )
        fig.data[0].update(lightposition=dict(x=3000, y=3000, z=10000))

        return dcc.Graph(figure=fig)

        # actors = []
        # for name in ["test2.stl"]:
        #     reader = vtk.vtkSTLReader()
        #     reader.SetFileName(name)
        #     mapper = vtk.vtkPolyDataMapper()
        #     mapper.SetInputConnection(reader.GetOutputPort())

        #     actor = vtk.vtkActor()
        #     actor.SetMapper(mapper)
        #     actor.GetProperty().SetColor((1, 0, 0))

        #     actors.append(actor)

        # # how to make use of actors here
        # mesh_state = to_mesh_state(reader.GetOutput())
        # vtk_view = dash_vtk.View(
        #     dash_vtk.GeometryRepresentation(
        #         dash_vtk.Mesh(state=mesh_state),
        #     )
        # )

        # return html.Div(
        #     id="dash_vtk_viewer",
        #     style={"height": "calc(80vh - 16px)", "width": "100%"},
        #     children=html.Div(vtk_view, style={"height": "100%", "width": "100%"}),
        # )

        # Load file
        # suppl_file_data = api_client.get_raw(
        #     relative_path="/supplementary_file/data",
        #     iri=selected_el.iri,
        # )

        # result = cq.importers.importStep(
        #     "./learning_factory_instance/binaries_import/hbw.step"
        # )

        # exporters.export(result, "hbw.vtp")

        # vs = OCP.IVtkOCC.IVtkOCC_Shape(w)
        # sd = OCP.IVtkVTK.IVtkVTK_ShapeData()
        # sm = OCP.IVtkOCC.IVtkOCC_ShapeMesher()
        # sm.Build(vs,sd)

        # res = sd.getVtkPolyData()

        # obj_file = "hbw.vtp"
        obj_file = "test2.stl"

        txt_content = None
        with open(obj_file, "r") as file:
            # txt_content = file.read()
            base64data = base64.b64encode(file.read())

        # base64data

        return html.Div(
            style={"width": "100%", "height": "400px"},
            children=[
                dash_vtk.View(
                    [
                        dash_vtk.GeometryRepresentation(
                            [
                                dash_vtk.Reader(
                                    vtkClass="vtkSTLReader",
                                    parseAsText=txt_content,
                                    parseAsArrayBuffer=base64data,
                                ),
                            ]
                        ),
                    ]
                )
            ],
        )

        # return html.Div(
        #     [
        #         dash_vtk.View(
        #             [
        #                 dash_vtk.VolumeRepresentation(
        #                     [
        #                         # GUI to control Volume Rendering
        #                         # + Setup good default at startup
        #                         dash_vtk.VolumeController(),
        #                         # Actual Imagedata
        #                         dash_vtk.ImageData(
        #                             dimensions=[5, 5, 5],
        #                             origin=[-2, -2, -2],
        #                             spacing=[1, 1, 1],
        #                             children=[
        #                                 dash_vtk.PointData(
        #                                     [
        #                                         dash_vtk.DataArray(
        #                                             registration="setScalars",
        #                                             values=list(range(5 * 5 * 5)),
        #                                         )
        #                                     ]
        #                                 )
        #                             ],
        #                         ),
        #                     ]
        #                 ),
        #             ]
        #         )
        #     ],
        #     style={"width": "100%", "height": "400px"},
        # )

    else:

        return datetime.now().isoformat()
