from sqlite3 import Cursor
import time
from typing import Any
import py2neo
import py2neo.ogm as ogm
from py2neo.errors import ConnectionBroken


from util.environment_and_configuration import get_environment_variable


class KnowledgeGraphPersistenceService(object):

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        KnowledgeGraphPersistenceService.__instance: KnowledgeGraphPersistenceService = (
            self
        )
        self.connected = False
        self._connect()

    def _connect(self):
        while not self.connected:
            try:
                print("Connecting to Neo4J...")
                self._graph = py2neo.Graph(
                    get_environment_variable(key="NEO4J_DB_HOST", optional=False),
                    name=get_environment_variable(key="NEO4J_DB_NAME", optional=False),
                )

                self._repo = ogm.Repository(
                    get_environment_variable(key="NEO4J_DB_HOST", optional=False),
                    name=get_environment_variable(key="NEO4J_DB_NAME", optional=False),
                )
                print("Successfully connected to Neo4J!")
                self.connected = True
            except py2neo.ConnectionUnavailable:
                print("Neo4J graph unavailable! Trying again in 10 seconds...")
                time.sleep(10)

    def graph_run(self, cypher: any) -> Cursor:
        """Executes the graph.run command.
        Handles connection errors.
        """
        while True:
            try:
                return self._graph.run(cypher)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_evaluate(self, cypher: Any) -> Any:
        """Executes the graph.evaluate command
        Handles connection errors.
        """
        while True:
            try:
                return self._graph.evaluate(cypher)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_push(self, subgraph: Any) -> None:
        """Executes the graph.push command
        Handles connection errors.
        """
        while True:
            try:
                return self._graph.push(subgraph)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_create(self, subgraph: Any) -> None:
        """Executes the graph.push command
        Handles connection errors.
        """
        while True:
            try:
                return self._graph.create(subgraph)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def graph_merge(self, subgraph: Any, label: Any | None = None) -> None:
        """Executes the graph.merge command
        Handles connection errors.
        """
        while True:
            try:
                return self._graph.merge(subgraph=subgraph, label=label)
            except ConnectionBroken:
                self.connected = False
                self._connect()

    def repo_match(self, model: Any, primary_value: Any | None = None) -> Any:
        """Executes the repo.match command
        Handles connection errors.
        """
        while True:
            try:
                return self._repo.match(model=model, primary_value=primary_value)
            except ConnectionBroken:
                self.connected = False
                self._connect()