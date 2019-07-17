import datetime


def json_default(value):
    if isinstance(value, datetime.datetime):
        return dict(year=value.year, month=value.month, day=value.day,
                    hour=value.hour, minute=value.minute,
                    second=value.second, microsecond=value.microsecond,
                    tzinfo=value.tzinfo)
    return value.__dict__
