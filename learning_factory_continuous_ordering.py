from datetime import datetime
import random
from threading import Thread
from time import sleep
import paho.mqtt.client as mqtt
import asyncio
import asyncua
import asyncua.ua
import asyncua.sync
import asyncio.exceptions
import time
import json
from util.log import logger

from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)

MQTT_HOST = get_environment_variable(
    key="FACTORY_MQTT_HOST", optional=True, default="host.docker.internal"
)
MQTT_PORT = get_environment_variable_int(
    key="FACTORY_MQTT_Port", optional=True, default="1883"
)

PIECE_TYPES = ["BLUE", "RED", "WHITE"]

mqtt_client = mqtt.Client()
mqtt_client.connect(host=MQTT_HOST, port=MQTT_PORT, keepalive=600)

last_stock_status = None


def on_message(client, userdata, message):
    global last_stock_status
    last_stock_status = str(message.payload.decode("utf-8"))


mqtt_client.on_message = on_message

mqtt_client.subscribe("f/i/stock", 2)

mqtt_thread = Thread(target=mqtt_client.loop_forever)
mqtt_thread.start()
# mqtt_client.loop_start()

OPC_UA_HOST = get_environment_variable(
    key="FACTORY_OPC_UA_HOST", optional=True, default="host.docker.internal"
)
OPC_UA_PORT = get_environment_variable_int(
    key="FACTORY_OPC_UA_PORT", optional=True, default="4840"
)
RECONNECT_DURATION = 10  # time to wait before trying to reconnect (in s)
KEEPALIVE_SUBSCRIPTION_SAMPLING_RATE = 1000  # sampling rate for keepalive subscriptions

opcua_client = None
asyncua_treadloop = asyncua.sync.ThreadLoop()
asyncua_treadloop.start()


class OpcuaHandler:
    def datachange_notification(self, node: asyncua.Node, val, data):
        """
        Callback for asyncua Subscriptions.
        This method will be called when the Client received a data change message from the Server.
        Class instance with event methods (see `SubHandler` base class for details).
        """
        pass


while opcua_client is None:
    try:
        opcua_client = asyncua.sync.Client(
            url=f"opc.tcp://{OPC_UA_HOST}:{OPC_UA_PORT}",
            tloop=asyncua_treadloop,
        )
    except asyncio.exceptions.TimeoutError:
        logger.info(
            "OPCUA connection timeout while initializing the connection. "
            f"Host: {OPC_UA_HOST}, port: {OPC_UA_PORT}. Retrying in {RECONNECT_DURATION} s ..."
        )
        time.sleep(RECONNECT_DURATION)

opcua_client.connect()

acknowledge_error_node: asyncua.sync.SyncNode = opcua_client.get_node(
    'ns=3;s="gtyp_Setup"."x_AcknowledgeButton"'
)
test_node: asyncua.sync.SyncNode = opcua_client.get_node(
    'ns=3;s="gtyp_HBW"."Horizontal_Axis"."di_Actual_Position"'
)

# Create subscription to avoid asyncua.sync.ThreadLoopNotRunning exceptions:
subscription = opcua_client.create_subscription(
    KEEPALIVE_SUBSCRIPTION_SAMPLING_RATE, handler=OpcuaHandler()
)
# Subscribe to one existing node.
# This subscription keeps the connection alive, even if the actual sensor reading happens via
# polling
subscription.subscribe_data_change(test_node)

sleep(10)

while True:
    # random_type = random.choice(PIECE_TYPES)

    # Acknowledge errors, if some occured. This sometimes happens (reason and further error information still to be discovered)
    dv = asyncua.ua.DataValue(asyncua.ua.Variant(True, asyncua.ua.VariantType.Boolean))
    # dv.ServerTimestamp = None
    # dv.SourceTimestamp = None
    acknowledge_error_node.set_value(dv)

    # Get available pieces:
    first_available_type = None
    try:
        if last_stock_status is not None:
            stock_dict = json.loads(last_stock_status)
            for storage in stock_dict["stockItems"]:
                if storage["workpiece"]["type"] != "":
                    first_available_type = storage["workpiece"]["type"]
                    break
    except KeyError:
        logger.info("KeyError in MQTT stock message!")

    formatted_time = datetime.now().isoformat()[:-3] + "Z"
    if first_available_type is not None:
        logger.info(f"Ordering piece ({first_available_type}, {formatted_time})")

        success_info = mqtt_client.publish(
            topic="f/o/order",
            payload='{"type":"'
            + first_available_type
            + '","ts":"'
            + formatted_time
            + '"}',
        )
    else:
        logger.info(f"No piece available! ({formatted_time})")

    sleep(200)
