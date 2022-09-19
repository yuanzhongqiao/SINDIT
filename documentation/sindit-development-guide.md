## Development setup

For this project, a devcontainer-setup for Visual Studio Code is implemented. It can be used together with SSH remote development if needed.

##### Requirements:

- Recent Linux operating system, e.g. Debian 11 (Some used DBMS-versions (Neo4J) are incompatible with, for example older CentOS systems)
- Docker and docker-compose installed

##### Development setup:

1. Check out this repository on the execution device (remote or local)
2. Open the folder on the development-client (local or with the VS Code remote development extension via SSH)
3. Reopen the folder as container with the remote containers extension
4. Reload the window after the container is fully loaded (as suggested by the initialization script, to apply the installed modules for auto-corrections)
5. Start the development databases manually with `docker-compose -f docker-compose.dev.yml up -d`. As there sometimes seem to be problems with creating the defined storage-mapping, execute this from the server-host, not within the devcontainer!

After this, use the run and debug functionalities of the IDE to execute the separate services. The run configuration is already set up in this repository.

If the DT-instance was not previously initialized, run the initialization script. E.g. via the run configuration `Learning factory instance: initialization`.

##### Code formatting:

The python formatting "black" is utilized and enforced by the IDE configuration. Auto-formatting is performed at every file-saving.

## Deployment and execution

This project is deployed via docker-compose. Run `docker-compose up -d` to start the digital twin with all required services.

If the DT-instance was not previously initialized, run the initialization scripts as described below (DT learning factory initialization script).

For the learning factory example, remember to access the VPN / make a port mappig via Teleport tsh in order to get an actual connection!

For updating the DT after pushing to the deployment branch, run manually on the workstation: `docker-compose down && git pull && sudo chmod 777 -R docker_mounted_storage && sudo chmod 777 -R backups && docker-compose build && docker-compose up -d`.

#### Exposed interfaces:

**Dashboard**

The main user interface (dashboard) of the digital twin can be reached at [http://localhost:8050/](http://localhost:8050/).

**REST API** The REST API is availlable at [http://localhost:8000/](http://localhost:8000/). 
Swagger documentation is availlable at [FastAPI - Swagger UI](http://localhost:8000/docs).

Webinterfaces of the used DBMS are available at [http://localhost:7475/](http://localhost:7475/) (Neo4J) and [http://localhost:8087/](http://localhost:8087/) (InfluxDB).

## Services:

In addition to the DBMS systems, the DT includes following services and scripts:

### DT-Backend service:

Sets up the realtime connections (OPC UA, MQTT) to persist timeseries data. Provides a REST API to access the assets of the factory including e.g. timeseries data (current and historic).

### DT-Frontend service:

Provides a dashboard and visualization of the DT via a web interface at [http://localhost:8050/](http://localhost:8050/). Utilizes the REST API

## DT learning factory initialization script:

Initializes the DT for the fischertechnik learning factory. Execute inside the standby container after starting the database services via:

`docker-compose exec sindit_dt_standby_environment python init_learning_factory_from_cypher_file.py`

After this, for the DT-services to connect to the newly created timeseries connections, restart the services with `docker-compose restart sindit_dt_backend sindit_dt_frontend` (simply restarting all containers does lead to the dependencies for database access not being resolved).

## Learning factory continuous ordering script:

Continuosly sends MQTT orders to the factory ordering a piece of random color. Execute inside the DT container after starting all services via:

`docker-compose exec sindit_dt_standby_environment python learning_factory_continuos_ordering.py`

Alternatively, run the preconfigured launch configuration in VS Code (Inside the dev-container).

## Backups

Making backups of the factory data is currently done manually by simply copying the mapped docker directories:

`sudo cp -R docker_mounted_storage/ backups/$(date +'%Y_%m_%d-%H_%M_%S')/` or inside the devcontainer-environment: `sudo cp -R docker_mounted_storage_devcontainer/ backups/$(date +'%Y_%m_%d-%H_%M_%S')/`

**Restoring:** To restore a specific backup, run:

1. `docker-compose down`
2. `sudo rm -R docker_mounted_storage`
3. `sudo cp -R backups/<THE_BACKUP_TO_RESTORE> docker_mounted_storage/`
4. `docker-compose up -d`sudo cp -R docker_mounted_storage_devcontainer/ backups/$(date +'%Y_%m_%d-%H_%M_%S')/

Or inside the devcontainer:

1. `docker-compose -f docker-compose.dev.yml down`
2. `sudo rm -R docker_mounted_storage_devcontainer`
3. `sudo cp -R backups/<THE_BACKUP_TO_RESTORE> docker_mounted_storage_devcontainer/`
4. `docker-compose -f docker-compose.dev.yml up -d`
5. Restart the backend afterwards.