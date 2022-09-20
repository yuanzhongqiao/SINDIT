import abc
from typing import Dict

from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionNode
from backend.runtime_connections.TimeseriesInput import TimeseriesInput
from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)


class RuntimeConnection(abc.ABC):
    """
    Base class for timeseries connections (OPCUA, MQTT, ...)
    One or several sensor inputs can be available via one connection over different
    topics.
    """

    def __init__(
        self,
        iri,
        host_environment_variable,
        port_environment_variable,
        user_environment_variable,
        key_environment_variable,
    ) -> None:
        super().__init__()

        self.active = False

        self.iri = iri

        self.host = get_environment_variable(
            key=host_environment_variable, optional=False
        )
        self.port = get_environment_variable_int(
            key=port_environment_variable, optional=False
        )

        self.user = (
            get_environment_variable(
                key=user_environment_variable, optional=True, default=None
            )
            if user_environment_variable is not None
            else None
        )

        self.key = (
            get_environment_variable(
                key=key_environment_variable, optional=True, default=None
            )
            if key_environment_variable is not None
            else None
        )

        self.timeseries_inputs: Dict[str, TimeseriesInput] = dict()

    @classmethod
    def from_runtime_connection_node(cls, node: RuntimeConnectionNode):
        return cls(
            iri=node.iri,
            host_environment_variable=node.host_environment_variable,
            port_environment_variable=node.port_environment_variable,
            user_environment_variable=node.user_environment_variable,
            key_environment_variable=node.key_environment_variable,
        )

    @abc.abstractmethod
    def start_connection(self):
        pass

    def is_active(self) -> bool:
        return self.active

    def remove_ts_input(self, iri: str):
        del self.timeseries_inputs[iri]

    @abc.abstractmethod
    def disconnect(self):
        """Disconnects and prepares for deletion"""

    @abc.abstractmethod
    def add_ts_input(self, ts_input: TimeseriesInput):
        pass
