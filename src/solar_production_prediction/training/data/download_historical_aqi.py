import argparse
import csv
import datetime
import dbm
import pathlib
import sys
import time

from ...weather_api import AirNowApi

WEB_SERVICE_HOURLY_REQUEST_LIMIT = 500
THROTTLE_TIME = 3  # seconds

DATE_START = datetime.date.fromisoformat("2017-12-13")
DATE_END = datetime.date.fromisoformat("2022-12-26")
TOTAL_DAYS = DATE_END - DATE_START

HISTORICAL_AQI_DB = pathlib.Path(__file__).parent / "historical_aqi_data" / "db"
HISTORICAL_AQI_DB.parent.mkdir(exist_ok=True, parents=True)

ONE_DAY_INCREMENT = datetime.timedelta(days=1)

## Exported constants
HISTORICAL_AQI_CSV_OUTFILE = str(
    pathlib.Path(__file__).parent
    / f"historical_aqi-{DATE_START.isoformat()}_to_{DATE_END.isoformat()}.csv"
)
FIELDNAME_DATE = "date"
FIELDNAME_PM25_DAILY_AVG = "pm25_daily_avg"
__all__ = (HISTORICAL_AQI_CSV_OUTFILE, FIELDNAME_DATE, FIELDNAME_PM25_DAILY_AVG)


def main(throttle_time: int = THROTTLE_TIME) -> None:
    api = AirNowApi()
    with dbm.open(str(HISTORICAL_AQI_DB), "c") as db:
        current = DATE_START
        while current <= DATE_END:
            progress = (TOTAL_DAYS - (DATE_END - current)).days
            sys.stdout.write(f"\r{progress:04d} / {TOTAL_DAYS.days}")
            sys.stdout.flush()

            db_key = current.isoformat()
            if db_key in db:
                current += ONE_DAY_INCREMENT
                continue

            aqi = api.get_historical_aqi(current)
            db[db_key] = str(aqi)
            current += ONE_DAY_INCREMENT
            time.sleep(throttle_time)

    sys.stdout.write("\n")
    sys.stdout.flush()


def write_to_csv():
    with dbm.open(str(HISTORICAL_AQI_DB), "r") as db:
        with open(HISTORICAL_AQI_CSV_OUTFILE, mode="w", newline="") as fd:
            field_names = [FIELDNAME_DATE, FIELDNAME_PM25_DAILY_AVG]
            writer = csv.DictWriter(fd, fieldnames=field_names)
            writer.writeheader()
            for date, aqi in db.items():
                writer.writerow(
                    {
                        "date": date.decode("utf-8"),
                        "pm25_daily_avg": float(aqi.decode("utf-8")),
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--throttle",
        dest="throttle_time",
        required=False,
        type=float,
        default=THROTTLE_TIME,
    )
    args = parser.parse_args()

    main(args.throttle_time)
    write_to_csv()
