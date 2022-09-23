import fastapi
from util.environment_and_configuration import get_environment_variable
from util.log import logger

"""
Fast API
Separated from service.py to avoid circular dependencies with endpoint files importing the "app" instance. 
"""
openapi_url = get_environment_variable(key="OPENAPI_URL", optional=True, default="/openapi.json")
logger.info(f"API: Using openapi_url: {openapi_url}")
app = fastapi.FastAPI(openapi_url=openapi_url)
