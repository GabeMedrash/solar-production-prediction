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


def get_forecast_for_hour(daily_forecast: DailyForecast, hour: int) -> HourlyForecast:
    forecast: typing.Iterator[HourlyForecast] = filter(
        lambda f: f.forecast_hour.hour == hour, daily_forecast.hourly
    )
    try:
        return next(forecast)
    except StopIteration:
        raise InsufficientHourlyForecastError(
            f"Can't find forecast for hour {hour}"
        ) from None


def get_weather_prediction(
    forecast: HourlyForecast, weather_prediction_variable: str
) -> int | float:
    prediction: typing.Iterator[WeatherPrediction] = filter(
        lambda p: p.type == weather_prediction_variable, forecast.predictions
    )
    try:
        return next(prediction).value
    except StopIteration:
        raise InsufficientHourlyForecastError(
            f"Can't find {weather_prediction_variable} prediction for hour {forecast.forecast_hour.hour}"
        ) from None


def predict(daily_forecast: DailyForecast, model: Model) -> SolarProductionPrediction:
    """
    Forecast is expected to be hourly forecast for one day.
    It may contain fewer than 24 forecast hours.
    """

    feature_vector: list[int | float] = []
    for field in model.fieldnames:
        if field == "energy_production_Wh":
            # This is the 'response variable'
            continue
        match field.split(OBSERVATION_NAME_AND_HOUR_SEPARATOR):
            case ["date"]:
                feature_vector.append(daily_forecast.date.month)
            case ["pm25_daily_avg"]:
                # TODO
                pass
            case [weather_prediction_variable, hour]:
                weather_forecast = get_forecast_for_hour(daily_forecast, int(hour))
                predicted_value = get_weather_prediction(
                    weather_forecast, weather_prediction_variable
                )
                feature_vector.append(predicted_value)
            case _:
                raise ValueError()

    solar_prediction = model.estimator.predict([feature_vector])
    return SolarProductionPrediction(
        date=daily_forecast.date, energy_production_Wh=solar_prediction[0]
    )
