from datetime import datetime


def neo4j_str_to_datetime(string: str) -> datetime:
    return datetime.fromisoformat(string.replace('"', "")[:-3])
