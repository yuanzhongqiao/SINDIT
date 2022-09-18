FROM python:3.10-slim-bullseye

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit

COPY . .

RUN ./container-requirements-initializer.sh

EXPOSE 8050
EXPOSE 8000
