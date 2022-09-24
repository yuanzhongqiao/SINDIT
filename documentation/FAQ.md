# FAQ / Frequent questions:

### Fischertechnik Training Factory Industry 4.0 24V

**The learning factory does suddenly not move anymore (VGR, HBW,...), but both MQTT and OPC UA are active and e.g. the camera can still be controlled and moved. Both ordering and putting new items in does not lead to any movement.**

> The factory sometimes produces errors that are not easily visible to the user.
> 
> To temporally fix the problem, press 'Acknowledge Errors' at the Node-RED Dashboard. Note that this Dashboard is not publicly available and can only be reached from within the local network of the factory.

### Development with the Devcontainer

**The port is already in use when (re-)launching either the backend or frontend.**

> E.g. for the fronten, you would see:
> ```Address already in use
> Port 8052 is in use by another program. Either identify and stop that program, or start the server with a different port.
> ```
> This happens e.g. if you close the terminal containing the process, without terminating it before.
> To solve it, you can run inside a terminal inside VS-Code:
> 
> 1. `apt install lsof`
> 2. `lsof -i:8052 | grep "(LISTEN)"`
> 
> That way you find the PID of the process.
> Then run the following to kill that process:
> 
> 3. `kill PID`
> 
> Do replace the port (8052) and the PID accordingly.