import datetime

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
for forecast in daily_forecasts:
    try:
        solar_production_prediction = predict(forecast, model)
        days_in_future = solar_production_prediction.date - today
        print(
            f"{days_in_future.days} day prediction ({solar_production_prediction.date}): {solar_production_prediction.energy_production_Wh}"
        )
    except InsufficientHourlyForecastError as exc:
        print(f"Can't make prediction for {forecast.date} because: {exc}")
