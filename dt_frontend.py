"""
Main entry point for the presentation layer
Separated from app.py to avoid circular dependencies with callback files importing the "app" instance. 
"""

from frontend.app import app
from util.log import logger

from frontend import page_layout

# Import callback files (indirectly used through annotation)

# pylint: disable=unused-import
# noinspection PyUnresolvedReferences
from frontend.navbar import navbar_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar import left_sidebar_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.extensions.similarity_pipeline_extension import (
    pipeline_extension_callbacks,
)

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.extensions.annotation_detection_extension import (
    annotation_extension_callbacks,
)

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_creation import (
    annotation_creation_callbacks,
)

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.visibility_settings import visibility_settings_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.global_information import global_information_callbacks

# noinspection PyUnresolvedReferences
from frontend.left_sidebar.datetime_selector import datetime_selector_callbacks

# noinspection PyUnresolvedReferences
from frontend.main_column.factory_graph import factory_graph_callbacks

# noinspection PyUnresolvedReferences
from frontend.right_sidebar import right_sidebar_callbacks

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.graph_selector_info import graph_selector_info_callbacks

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_callbacks,
)

# noinspection PyUnresolvedReferences
from frontend.right_sidebar.node_data_tab.file_visualization import (
    file_visualization_callbacks,
)

from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)


# #############################################################################
# Launch frontend
# #############################################################################

server = app.server
# Initialize layout
logger.info("Initializing app layout...")
app.layout = page_layout.get_layout()
logger.info("Finished initializing the app layout.")

FRONTEND_HOST = get_environment_variable("FRONTEND_HOST")
FRONTEND_PORT = get_environment_variable_int("FRONTEND_PORT")
logger.info(f"Starting the frontend at host: {FRONTEND_HOST}, port: {FRONTEND_PORT}")

if __name__ == "__main__":

    app.run(
        host=FRONTEND_HOST,
        debug=False,
        port=FRONTEND_PORT,
        use_reloader=False,
    )
