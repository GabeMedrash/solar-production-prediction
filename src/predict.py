import dataclasses
import datetime
import typing

from .external_data import (
    DailyForecast,
    HourlyForecast,
    WeatherPrediction,
)
from .model import (
    OBSERVATION_NAME_AND_HOUR_SEPARATOR,
    Model,
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
        match field.split(OBSERVATION_NAME_AND_HOUR_SEPARATOR):
            case ["date"]:
                evidence.append(daily_forecast.date.month)
            case ["pm25_daily_avg"]:
                # TODO
                pass
            case [prediction_type, hour]:
                forecast = _get_forecast_for_hour(int(hour))
                prediction = _get_weather_prediction(forecast, prediction_type)
                evidence.append(prediction.value)
            case _:
                raise ValueError()

    solar_prediction = model.estimator.predict([evidence])
    return SolarProductionPrediction(
        date=daily_forecast.date, energy_production_Wh=solar_prediction[0]
    )
