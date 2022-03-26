from datetime import datetime
from datetime import timezone
import pytz

FRANCE = pytz.timezone('Europe/Paris')


def _format_date(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_date(year: int, month: int = 1, day: int = 1) -> str:
    return _format_date(datetime(year, month, day, tzinfo=FRANCE)
                        .astimezone(timezone.utc))


def get_date_now() -> str:
    return _format_date(datetime.now(FRANCE).astimezone(timezone.utc))


if __name__ == '__main__':
    """Check that it works"""
    print(get_date(2022))
    print(get_date_now())
