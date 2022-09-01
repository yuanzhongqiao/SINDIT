from datetime import datetime


def neo4j_str_to_datetime(string: str) -> datetime:
    return datetime.fromisoformat(string.replace('"', "")[:-3])


def neo4j_str_or_datetime_to_datetime(date_time: str | datetime) -> datetime:
    if isinstance(date_time, datetime):
        return date_time
    else:
        return neo4j_str_to_datetime(date_time)
