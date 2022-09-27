# Installation, Requirements & How to Run SINDIT

## Requirements
- **Operating system**: While it is highly recommended to both run and develop SINDIT on a up-to-date Linux distribution, other operating systems like Mac-OS and Windows also work with reduced performance.
- **Docker**: SINDIT is fully developed with Docker. It was tested with docker versions between 20.10.12 and 20.10.17. Newer versions will likely work as well. Slightly older versions may also work. On Windows and Mac-OS, use Docker Desktop (with the WSL 2.0 back-end in the case of Windows).
- **docker-compose**: Compose should also be used both for development and for running SINDIT in a smaller scale (The larger demo-instance is deployed with Kubernetes instead, see below). SINDIT was tested with docker-compose version between 1.29.2 and v2.10.2, other versions may or may not also work. The docker-compose file specification 2.4 has to be supported. For the development with the devcontainer, the "docker-compose" command should be natively available. If you can only run "docker compose" on you terminal, you will need to do at least some manual reconfigurations in order to launch the devcontainer successfully.
- **IDE**: For developing and debugging SINDIT, only one IDE is currently supported: Visual Studio Code. See below for instructions. Running and debugging with other IDEs not supporting devcontainers will require you to find a different solution in order to install all the requirements used by SINDIT and is not recommended. Installing them without a containerized setup should be avoided. 
- **Memory**: With five seperate containers and three database-systems, SINDIT has some increased memory requirements. On Windows and Mac-OS, the consumption will likely be even higher, as the docker-containers run not natively. On Windows, WSL2 usually does not free the used memory again after stopping (or even dropping) the containers. You likely need to restart at least WSL2 to recover your memory.
    - Executing SINDIT as application:
        - It is recommended to have at least 10 GB of free memory just for running SINDIT with `docker-compose.yml`.
        - There is a separate `docker-compose.low-memory.yml` limiting the total usage of the containers to 5,5 GB. Do not expect to use this with large data-sets.
    - Developing and debugging SINDIT:
        - For the devcontainer-setup, you are recommended to have at least 12 GB of free memory just for the containers.
        - With the manual changes described below, you can drop this limit to 9 GB.
        - If you can not meet this limits on your local development device, it is highly recommended to use the `Remote - SSH` extension of Visual Studio Code in order to connect to a more powerful server and use your local device only as client.
- **Free Ports**: The utilized ports of SINDIT can easily be changed. Without changes, the following ports will be required to be free:
    - Executing SINDIT as application:
        - 8050: SINDIT frontend
        - 8000: SINDIT API
        - 8087: Influx DB
        - 7475: Neo4J web interface
        - 7688: Neo4J
        - 9000: Minio S3
        - 9097: Minio S3 web interface
    - Developing on SINDIT with the devcontainer:
        - 8052: SINDIT frontend
        - 8001: SINDIT API
        - 8086: Influx DB
        - 7476: Neo4J web interface
        - 7689: Neo4J
        - 9001: Minio S3
        - 9098: Minio S3 web interface
- **(fischertechnik Training Factory 4.0)**: SINDIT was developed with the training factory as running example. The real-time aspects can be tried with that factory, or you can simply run SINDIT without it. It will not find the connections, but run nevertheless. SINDIT can also be utilized for other factories by creating a new initialization script and altering the environment variables accordingly.

## How to Run SINDIT

### Run with docker-compose and pre-build image:
This project is run via docker-compose. Run `docker-compose up -d` inside the repository to start the Digital Twin with all required services.

At the first start, this will pull the image used for the frontend and backend containers and for the databases. Use a good network, as the images are not small.

To stop the containers, run `docker-compose stop`. 

To destroy the containers but keep the images and data, run `docker-compose down`.

To destroy the containers and remove the downloaded images, run `docker-compose down --rmi all`.

### Low-memory setup:

There are separate compose files prepared with lower memory limits. Use the `-f docker-compose.low-memory.yml` option. E.g. `docker-compose -f docker-compose.low-memory.yml up -d`.


### Build the image locally from scratch:

There are separate compose files for building the main SINDIT image locally. Use the `-f docker-compose.build-local.yml` option equivalent to the low memory setup.

To combine this with the low memory setup, use `-f docker-compose.low-memory.build-local.yml`

At the first start, this will build the image used for the frontend and backend containers and pull images for the databases. This will take about 10 minutes, as there are many requirements being installed inside the container.

To later rebuild the image, run `docker-compose build`. If you updated the repository, run this in order to actually execute the new version!

To destroy the containers and remove the local built image, run `docker-compose down --rmi local`. The `--rmi all` option includes this.

## Development & Debugging

### Development with the Devcontainer:
A Visual Studio Code Devcontainer is set up and ready to be used. You can set up your development environment in few steps:

1. Check out this repository on the execution device (where your code will actually be run: remote or local).
2. Open the folder on the development-client with Visual Studio Code (local or with the VS Code `Remote SSH` extension via SSH if you want to use a more powerful server for remote development).
3. Reopen the folder as container with the `Dev Containers` extension. Likely, VS Code will ask you actively to do this. If not, open the command panel in VS Code (F1) and execute `> Remote-Containers: Rebuild Container`.
4. Reload the window after the container is fully loaded (as suggested by the initialization script, to apply the installed modules for auto-corrections).
5. Start the development databases manually with `docker-compose -f docker-compose.dev.yml up -d`. As there sometimes seem to be problems with creating the defined storage-mapping, execute this in a separate shell on your execution device, not from within the devcontainer with the VS-Code terminal!

After this, use the run and debug functionalities of the IDE to execute the separate services. The run configuration is already set up in this repository.

Normally, VS Code mapps the ports opened by the code on its own and exposes it to you client computer after a short while of running. This way, you will be able to open the SINDIT dashboard in your browser with `localhost:8052`. You can manually set up the mapping within the 'PORTS' tab of VS-Code so they are immediately reachable.

It is not recommended to develop on SINDIT without a container-setup.

### Devcontainer: Low memory setup:

For debugging SINDIT, you need more memory as compared to just run it. To minimize the amount, you can run the databases in a version with lower limits with `docker-compose -f docker-compose.dev.low-memory.yml up -d`. If you want to save even more memory, manually override the mem_limit in `.devcontainer/docker-compose.yml` Give it at least 6 GB instead of the normal 8 GB in order to run properly.

### Code formatting:

The python formatting "black" is utilized and enforced by the IDE configuration. Auto-formatting is performed at every file-saving.

For the learning factory example, remember to access the VPN / make a port mappig via Teleport tsh in order to get an actual connection!


## Exposed interfaces:

**Dashboard**

The main user interface (dashboard) of the digital twin can be reached at [http://localhost:8050/](http://localhost:8050/) or [http://localhost:8052/](http://localhost:8052/) if run in the devcontainer.

**REST API** The REST API is availlable at [http://localhost:8000/](http://localhost:8000/). 
Swagger documentation is availlable at [FastAPI - Swagger UI](http://localhost:8000/docs).

The port-number for the devcontainer is 8002.

**Webinterfaces** of the used DBMS are available at [http://localhost:7475/](http://localhost:7475/) (Neo4J), [http://localhost:8087/](http://localhost:8087/) (InfluxDB) and [http://localhost:9097/](http://localhost:9097/) (Minio S3).

Find the ports for the devcontainer on top of this file.

## Main Services of SINDIT:

In addition to the DBMS systems, the DT includes following services and scripts:

### DT-Backend service:

Sets up the realtime connections (OPC UA, MQTT) to persist timeseries data. Provides a REST API to access the assets of the factory including e.g. timeseries data (current and historic).

### DT-Frontend service:

Provides a dashboard and visualization of the DT via a web interface at [http://localhost:8050/](http://localhost:8050/). Utilizes the REST API

## Additional scripts:

### Learning factory continuous ordering script:

Continuosly sends MQTT orders to the factory ordering a piece of random color. Execute inside the DT container after starting all services via:

`docker-compose exec sindit_dt_backend python learning_factory_continuos_ordering.py`

Alternatively, run the preconfigured launch configuration in VS Code (Inside the dev-container).

## Connecting to a physical fischertechnik Training Factory Industry 4.0:

The required setup is highly dependent on your local network situation. You will likely need to access the router of the factory in order to open ports used for MQTT and OPC UA.

## Changing configuration and environmental variables:

For many things, SINDIT uses environmental variables. There also is a file `./environment_and_configuration/sindit_config.cfg` allowing for some customizations. Most important, the used hostnames, ports and credentials are defined with environmental variables.

For the start, there are .env files inside `./environment_and_configuration` that contain default values and are used by either docker-copmose or the devcontainer. Change the ports etc. there to your needs.

**Important**: This files serve only as a development setup and are not supposed to be used for production! Make sure to keep credentials used for actual valuable data in a secure place!

## Kubernetes Deployment:

In `./kubernetes_deployment/helm-chart`, you can find some templates that can be used for your deployment.