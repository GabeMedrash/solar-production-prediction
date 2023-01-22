"""
Combine solar production data (energy produced per day) with historical weather data
(hourly) to produce joined dataset ready for training.
Output CSV has the date and energy production as first two columns,
a daily average of AQI for that day, then a repeating set of columns for observed weather at specific hours.

Example output:
`date | energy_production_Wh | pm25_daily_avg | temp_7 | humidity_7 | cloudcover_7 | ... | temp_14 | humidity_14 | cloudcover_14 | ...`

To run:
`/venv/bin/python src/model/data/create_training_set.py`
"""
import csv
import dataclasses
import datetime
import locale
import pathlib
import typing

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


### Solar production records
SOLAR_PRODUCTION = (
    pathlib.Path(__file__).parent / "solar_production-20171213_to_20221226.csv"
)


class SolarProductionRecord(typing.TypedDict):
    date: datetime.date
    energy_production_Wh: int


solar_production_records: list[SolarProductionRecord] = []

with open(SOLAR_PRODUCTION, mode="r", newline="") as fd:
    csv_reader = csv.DictReader(fd)
    for row in csv_reader:

        def get_field_and_format(field, formatter):
            return formatter(row[field])

        record: SolarProductionRecord = {
            "date": get_field_and_format(
                "date", lambda ds: datetime.datetime.strptime(ds, "%m/%d/%Y").date()
            ),
            "energy_production_Wh": get_field_and_format(
                "energy_produced_Wh", locale.atoi
            ),
        }

        solar_production_records.append(record)


### Historical weather records
WEATHER = pathlib.Path(__file__).parent / "visualcrossing-20171201_to_20221229.csv"
DIMS: list[tuple[str, typing.Callable]] = [
    ("temp", float),
    ("humidity", float),
    ("cloudcover", float),
]


@dataclasses.dataclass
class WeatherRecordHourly:
    datetime: datetime.datetime
    observations: list[tuple[str, float]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class WeatherRecordDaily:
    date: datetime.date
    hours: list[WeatherRecordHourly] = dataclasses.field(default_factory=list)


weather_records: dict[datetime.date, WeatherRecordDaily] = {}
with open(WEATHER, mode="r", newline="") as fd:
    csv_reader = csv.DictReader(fd)

    for row in csv_reader:

        hour_datetime = datetime.datetime.fromisoformat(row["datetime"])
        weather_record_for_hour = WeatherRecordHourly(hour_datetime)

        for field, formatter in DIMS:
            weather_record_for_hour.observations.append((field, formatter(row[field])))

        if hour_datetime.date() not in weather_records:
            weather_record_for_date = WeatherRecordDaily(hour_datetime.date())
            weather_records[hour_datetime.date()] = weather_record_for_date

        weather_record_for_date = weather_records[hour_datetime.date()]
        weather_record_for_date.hours.append(weather_record_for_hour)


### Historical AQI
AQI = pathlib.Path(__file__).parent / "historical_aqi-2017-12-13_to_2022-12-26.csv"
aqi_records: dict[datetime.date, float] = {}
with open(AQI, mode="r", newline="") as fd:
    csv_reader = csv.DictReader(fd)

    for row in csv_reader:
        date = datetime.date.fromisoformat(row["date"])
        aqi = float(row["pm25_daily_avg"])
        aqi_records[date] = aqi


### Joined dataset
OUTFILE = pathlib.Path(__file__).parent / "preprocessed_training_data.csv"

MIN_HOUR = 7  # 7am
MAX_HOUR = 19  # 7pm
OBSERVATION_NAME_AND_HOUR_SEPARATOR = "|"
joined_records = []
for solar_production_record in solar_production_records:
    joined = {
        **solar_production_record,
    }

    aqi_record_for_date = aqi_records[solar_production_record["date"]]
    # joined["pm25_daily_avg"] = aqi_record_for_date

    weather_record_for_date = weather_records[solar_production_record["date"]]
    for weather_record_for_hour in weather_record_for_date.hours:
        hour = weather_record_for_hour.datetime.hour
        if MIN_HOUR <= hour <= MAX_HOUR:
            joined = {
                **joined,
            }
            for obs_name, obs_value in weather_record_for_hour.observations:
                if obs_name != "datetime":
                    formatted_key = (
                        f"{obs_name}{OBSERVATION_NAME_AND_HOUR_SEPARATOR}{hour}"
                    )
                    joined[formatted_key] = obs_value

    joined_records.append(joined)


with open(OUTFILE, mode="w", newline="") as fd:
    field_names = joined_records[0].keys()
    writer = csv.DictWriter(fd, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(joined_records)
