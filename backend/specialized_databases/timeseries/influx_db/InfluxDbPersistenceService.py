from datetime import datetime, timedelta
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
import pandas as pd
from urllib3.exceptions import ReadTimeoutError, NewConnectionError, ConnectTimeoutError
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

from backend.exceptions.IdNotFoundException import IdNotFoundException
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)

READING_FIELD_NAME = "reading"


class InfluxDbPersistenceService(TimeseriesPersistenceService):
    """ """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bucket = self.group

        self._last_reading_dropped = False

        self._client: InfluxDBClient = InfluxDBClient(
            url=self.host + ":" + self.port,
            token=self.key,
            org=self.database,
            verify_ssl=self.key is not None,
        )

        # Synchronous mode to allow live data processing from the database
        # Consider batch mode if having performance issues
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api = self._client.query_api()

    # override
    def write_measurement(
        self, id_uri: str, value: float | bool | str, reading_time: datetime = None
    ):
        """
        Writes the given value to the standard bucket into the measurement according to the id_uri into a field
        called 'reading'.
        When no reading time is given, the current database time is being used.
        :param id_uri:
        :param value:
        :param reading_time:
        :return:
        """

        record = Point(measurement_name=id_uri).field(
            field=READING_FIELD_NAME, value=value
        )
        if reading_time is not None:
            record.time(reading_time)
        # pylint: disable=W0703
        try:
            self._write_api.write(bucket=self.bucket, record=record)
            if self._last_reading_dropped:
                print("Writing of time-series readings working again.")
            self._last_reading_dropped = False
        except Exception:
            # Using generic exception on purpose, since there are many different ones occuring, that
            # all require the same handling
            if not self._last_reading_dropped:
                print(
                    "Time-series reading dropped: Database not available (ReadTimeoutError). "
                    "Will notify when successful again."
                )
            self._last_reading_dropped = True
            # continue with new readings (drop this one)

    def _timerange_query(self, begin_time: datetime | None, end_time: datetime | None):
        # Max 10 years as InfluxDB does not support unbounded queries
        datetime_min = (
            (datetime.now() - timedelta(days=356 * 10)).astimezone().isoformat()
        )
        datetime_max = datetime.now().astimezone().isoformat()

        if begin_time is not None and end_time is not None:
            range_query = f"|> range(start: {begin_time.astimezone().isoformat()}, stop: {end_time.astimezone().isoformat()})"
        elif begin_time is None and end_time is not None:
            range_query = f"|> range(start: {datetime_min}, stop: {end_time.astimezone().isoformat()})"
        elif begin_time is None and end_time is not None:
            range_query = f"|> range(start: {begin_time.astimezone().isoformat()}, stop: {datetime_max})"
        else:
            range_query = f"|> range(start: {datetime_min}, stop: {datetime_max})"

        return range_query

    # override
    def read_period_to_dataframe(
        self,
        id_uri: str,
        begin_time: datetime | None,
        end_time: datetime | None,
        aggregation_window_ms: int | None,
    ) -> pd.DataFrame:
        """
        Reads all measurements from the sensor with the given ID in the time period
        :param id_uri:
        :param begin_time:
        :param end_time:
        :return: Dataframe containing all measurements in that period
        :raise IdNotFoundException: if the id_uri is not found
        """
        range_query = self._timerange_query(begin_time, end_time)

        if isinstance(aggregation_window_ms, int) and aggregation_window_ms != 0:
            query = (
                f'from(bucket: "{self.bucket}") \n'
                f"{range_query} \n"
                f'|> filter(fn: (r) => r["_measurement"] == "{id_uri}") \n'
                f"|> aggregateWindow(every: {aggregation_window_ms}ms, fn: first, createEmpty: false)\n"
                f'|> keep(columns: ["_time", "_value"]) \n'
                '|> rename(columns: {_time: "time", _value: "value"})'
            )
        else:
            query = (
                f'from(bucket: "{self.bucket}") \n'
                f"{range_query} \n"
                f'|> filter(fn: (r) => r["_measurement"] == "{id_uri}") \n'
                f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") \n'
                f'|> keep(columns: ["_time", "{READING_FIELD_NAME}"]) \n'
                '|> rename(columns: {_time: "time", reading: "value"})'
            )

        while True:
            try:
                df = self._query_api.query_data_frame(query=query)

                # Dataframe cleanup
                df.drop(columns=["result", "table"], axis=1, inplace=True)
                # df.rename(
                #     columns={"_time": "time", READING_FIELD_NAME: "value"}, inplace=True
                # )
                # df.rename(columns={"_time": "time", "_value": "value"}, inplace=True)

                return df

            except KeyError:
                # id_uri not found
                raise IdNotFoundException
            except NewConnectionError:
                # Waiting for reconnect...
                pass

    # override
    def count_entries_for_period(
        self, id_uri: str, begin_time: datetime, end_time: datetime
    ) -> int:
        """
        Counts the measurement entries from the sensor with the given ID in the time period
        :param id_uri:
        :param begin_time:
        :param end_time:
        :return: number of entries
        :raise IdNotFoundException: if the id_uri is not found
        """
        warnings.simplefilter("ignore", MissingPivotFunction)
        range_query = self._timerange_query(begin_time, end_time)

        query = (
            f'from(bucket: "{self.bucket}") \n'
            f"{range_query} \n"
            f'|> filter(fn: (r) => r["_measurement"] == "{id_uri}") \n'
            f'|> count(column: "_value") \n'
            f'|> keep(columns: ["_value"])'
        )

        while True:
            # pylint: disable=W0703
            try:
                df: pd.DataFrame = self._query_api.query_data_frame(query=query)

                return int(df["_value"][0]) if not df.empty else 0

            except KeyError:
                # id_uri not found
                raise IdNotFoundException
            except Exception:
                # Using generic exception on purpose, since there are many different ones occuring, that
                # Waiting for reconnect...
                pass
