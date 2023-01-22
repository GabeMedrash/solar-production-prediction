"""
To run:
`$ venv/bin/python -m src.bin.predict`
"""
import datetime

import duckdb

from src.external_data import NoaaApi
from src.model import model
from src.persistence import PREDICTIONS_DB_PATH
from src.predict import (
    InsufficientHourlyForecastError,
    predict,
)

if model is None:
    raise TypeError("model must be trained and exported from the `model` sub-package")

date_of_prediction = datetime.date.today()

# Get current weather forecast
noaa_api = NoaaApi()
daily_forecasts = noaa_api.get_forecast()


db_con = duckdb.connect(PREDICTIONS_DB_PATH)
for forecast in daily_forecasts:
    try:
        # predict
        solar_production_prediction = predict(forecast, model)
        days_in_future = solar_production_prediction.date - date_of_prediction
        print(
            f"{days_in_future.days} day prediction ({solar_production_prediction.date}): {solar_production_prediction.energy_production_Wh}"
        )

        # persist
        db_con.execute(
            "INSERT INTO predictions VALUES (?, ?, ?, ?, ?)",
            [
                solar_production_prediction.date,
                date_of_prediction,
                model.version,
                solar_production_prediction.energy_production_Wh,
                None,
            ],
        )
    except duckdb.ConstraintException as exc:
        # TODO: Make use of UPSERT once supported by DuckDb (https://github.com/duckdb/duckdb/pull/5866)
        print(
            f"Prediction already made for {solar_production_prediction.date} on {date_of_prediction} using model {model.version}"
        )

    except InsufficientHourlyForecastError as exc:
        print(f"Can't make prediction for {forecast.date} because: {exc}")
