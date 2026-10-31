import datetime

from zoneinfo import ZoneInfo

def get_datetime(value):
    dt = datetime.datetime.fromisoformat(str(value))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Europe/Berlin"))

    return dt