FROM python:3.10-slim-bullseye

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit

COPY container-requirements-initializer.sh ./
COPY requirements.txt ./
RUN ./container-requirements-initializer.sh

COPY assets assets
COPY backend backend
COPY environment_and_configuration environment_and_configuration
COPY frontend frontend
COPY graph_domain graph_domain
COPY learning_factory_instance learning_factory_instance
COPY util util
COPY dt_backend.py ./
COPY dt_frontend.py ./
COPY init_learning_factory_from_cypher_file.py ./
COPY learning_factory_continuous_ordering.py ./
COPY similarity* ./

EXPOSE 8050
EXPOSE 8000
