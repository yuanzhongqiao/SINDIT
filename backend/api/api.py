import fastapi
from util.environment_and_configuration import get_environment_variable
from util.log import logger

"""
Fast API
Separated from service.py to avoid circular dependencies with endpoint files importing the "app" instance. 
"""
root_path = get_environment_variable(key="API_ROOT_PATH", optional=True, default="/")
openapi_path = get_environment_variable(key="OPENAPI_URL", optional=True, default="/openapi.json")
logger.info(f"API: Root path set to: {root_path}")
logger.info(f"API: Openapi path set to: {openapi_path}")
app = fastapi.FastAPI(root_path=root_path, openapi_url=openapi_path)