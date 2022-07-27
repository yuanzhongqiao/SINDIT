from datetime import datetime
import random
from time import sleep
import paho.mqtt.client as mqtt

from util.environment_and_configuration import get_environment_variable, get_environment_variable_int

HOST = get_environment_variable(
    key="FACTORY_MQTT_HOST", optional=True, default="host.docker.internal"
)
PORT = get_environment_variable_int(key="FACTORY_MQTT_Port", optional=True, default="1883")

TYPES = ["BLUE", "RED", "WHITE"]

mqtt_client = mqtt.Client()
mqtt_client.connect(host=HOST, port=PORT, keepalive=600)



while True:
    formatted_time = datetime.now().isoformat()[:-3] + "Z"
    random_type = random.choice(TYPES)
    
    print(f"Ordering piece ({random_type}, {formatted_time})")
    
    success_info = mqtt_client.publish(
        topic="f/o/order", payload='{"type":"' + random_type + '","ts":"' + formatted_time + '"}'
    )
    
    sleep(200)
