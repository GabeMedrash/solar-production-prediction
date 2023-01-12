import dataclasses
import datetime
import pdb
import typing

from .training import KEY_HOUR_SEPARATOR, Model
from .weather_api import (
    DailyForecast,
    HourlyForecast,
    WeatherPrediction,
)


@dataclasses.dataclass
class SolarProductionPrediction:
    date: datetime.date
    energy_production_Wh: float


class InsufficientHourlyForecastError(Exception):
    pass


def predict(daily_forecast: DailyForecast, model: Model) -> SolarProductionPrediction:
    """
    Forecast is expected to be hourly forecast for one day.
    It may contain fewer than 24 forecast hours.
    """

    def _get_forecast_for_hour(hour: int) -> HourlyForecast:
        forecast: typing.Iterator[HourlyForecast] = filter(
            lambda f: f.forecast_hour.hour == hour, daily_forecast.hourly
        )
        try:
            return next(forecast)
        except StopIteration:
            # pdb.set_trace()
            raise InsufficientHourlyForecastError(
                f"Can't find forecast for hour {hour}"
            ) from None

    def _get_weather_prediction(
        forecast: HourlyForecast, prediction_type
    ) -> WeatherPrediction:
        prediction: typing.Iterator[WeatherPrediction] = filter(
            lambda p: p.type == prediction_type, forecast.predictions
        )
        try:
            return next(prediction)
        except StopIteration:
            raise InsufficientHourlyForecastError(
                f"Can't find {prediction_type} prediction for hour {hour}"
            ) from None

    evidence: list[int | float] = []
    for field in model.fieldnames:
        if field == "energy_production_Wh":
            continue
        match field.split(KEY_HOUR_SEPARATOR):
            case ["date"]:
                evidence.append(daily_forecast.date.month)
            case [prediction_type, hour]:
                forecast = _get_forecast_for_hour(int(hour))
                prediction = _get_weather_prediction(forecast, prediction_type)
                evidence.append(prediction.value)
            case _:
                pdb.set_trace()
                raise ValueError()

    solar_prediction = model.predictor.predict([evidence])
    return SolarProductionPrediction(
        date=daily_forecast.date, energy_production_Wh=solar_prediction[0]
    )
