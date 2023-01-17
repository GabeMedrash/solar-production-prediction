import datetime

import duckdb

from .model import model
from .predict import (
    InsufficientHourlyForecastError,
    predict,
)
from .prediction import PREDICTIONS_DB_PATH
from .weather_api import NoaaApi

if model is None:
    raise TypeError("model must be trained and exported from the `model` sub-package")

date_of_prediction = datetime.datetime.now().date()

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

    except InsufficientHourlyForecastError as exc:
        print(f"Can't make prediction for {forecast.date} because: {exc}")
