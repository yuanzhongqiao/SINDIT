from pymemcache.client import base
import subprocess
from util.log import logger

memcache = base.Client(("localhost", 11211))

try:
    memcache.set("test-key", "test-value")
except ConnectionRefusedError:
    # Run memcache
    logger.info("Starting memcached inter-process cache on port 11211...")
    subprocess.Popen(["memcached", "-u", "root"])
