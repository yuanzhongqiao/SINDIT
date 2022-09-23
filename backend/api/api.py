import fastapi
from util.environment_and_configuration import get_environment_variable

"""
Fast API
Separated from service.py to avoid circular dependencies with endpoint files importing the "app" instance. 
"""
openapi_url = get_environment_variable(key="OPENAPI_URL", optional=True, default="/openapi.json")
app = fastapi.FastAPI(openapi_url=openapi_url)
