import datetime
import dbm
import json
import pathlib

from .predict import (
    InsufficientHourlyForecastError,
    predict,
)
from .training import train
from .weather_api import NoaaApi

today = datetime.datetime.now().date()

# Get trained model
model = train()

# Get current weather forecast
noaa_api = NoaaApi()
daily_forecasts = noaa_api.get_forecast()

PREDICTIONS_DB = pathlib.Path(__file__).parent / "predictions" / "db"
PREDICTIONS_DB.parent.mkdir(exist_ok=True, parents=True)

with dbm.open(str(PREDICTIONS_DB), "c") as db:
    # save model statistics
    model_key = f"model_v{model.version}"
    if not model_key in db:
        db[model_key] = model.to_json()

    for forecast in daily_forecasts:
        try:
            # predict
            solar_production_prediction = predict(forecast, model)
            days_in_future = solar_production_prediction.date - today
            print(
                f"{days_in_future.days} day prediction ({solar_production_prediction.date}): {solar_production_prediction.energy_production_Wh}"
            )

            # persist
            key = solar_production_prediction.date.isoformat()
            record = json.loads(db.get(key, b"{}"))
            record[
                f"{days_in_future.days}"
            ] = solar_production_prediction.energy_production_Wh
            db[key] = json.dumps(record)

        except InsufficientHourlyForecastError as exc:
            print(f"Can't make prediction for {forecast.date} because: {exc}")
