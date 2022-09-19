FROM python:3.10-slim-bullseye

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit

COPY container-requirements-initializer.sh ./
COPY requirements.txt ./
RUN ./container-requirements-initializer.sh

COPY . .

EXPOSE 8050
EXPOSE 8000
