import dataclasses
import datetime

from ..env import Env
from .http_client import HttpClient

# Dimensions of the weather forecast to use as part of solar production prediction. Tuple order:
#   (Dimension name, XML tag, XML "type" attribute, formatter)
DIMS = [
    ("temp", "temperature", "hourly", float),
    ("cloudcover", "cloud-amount", None, float),
    ("humidity", "humidity", "relative", float),
]


@dataclasses.dataclass
class WeatherPrediction:
    type: str
    value: int | float


@dataclasses.dataclass
class HourlyForecast:
    forecast_hour: datetime.datetime
    predictions: list[WeatherPrediction] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class DailyForecast:
    date: datetime.date
    hourly: list[HourlyForecast] = dataclasses.field(default_factory=list)


class XMLParseError(Exception):
    pass


class NoaaApi:
    _env: Env
    _http_client: HttpClient

    def __init__(
        self, http_client: HttpClient = HttpClient(), env: Env = Env()
    ) -> None:
        self._env = env
        self._http_client = http_client

    def get_forecast(self) -> list[DailyForecast]:
        """
        Return 168hr point forecast, grouped by date

        lxml ElementBase docs:
        https://lxml.de/apidoc/lxml.etree.html#lxml.etree.ElementBase
        """
        hourly_forecasts: list[HourlyForecast] = []

        lat, lon = self._env.latlong()
        root = HttpClient.get_xml(
            f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}&FcstType=digitalDWML"
        )

        time_layout = root.find("./data/time-layout")
        one_hour = datetime.timedelta(hours=1)
        forecast_hour_start = None
        for element in time_layout.iter(("start-valid-time", "end-valid-time")):
            if element.tag == "start-valid-time":
                forecast_hour_start = datetime.datetime.fromisoformat(element.text)
            if element.tag == "end-valid-time":
                if forecast_hour_start is None:
                    raise XMLParseError(
                        "Visited an 'end-valid-time' element before a 'start-valid-time' element."
                    )
                forecast_hour_end = datetime.datetime.fromisoformat(element.text)
                if forecast_hour_end - forecast_hour_start != one_hour:
                    raise XMLParseError(
                        f"Time step between 'start-valid-time' ({forecast_hour_start}) and 'end-valid-time' ({forecast_hour_end}) is not one hour"
                    )
                hourly_forecasts.append(HourlyForecast(forecast_hour_start))

        parameters = root.find("./data/parameters")
        for name, el_tag, el_type, formatter in DIMS:
            xpath_expression = f"//{el_tag}"
            if el_type is not None:
                xpath_expression = f'{xpath_expression}[@type="{el_type}"]'
            parameter = parameters.xpath(xpath_expression)[0]
            i = 0
            for value in parameter.iter("value"):
                hour_forecast = hourly_forecasts[i]
                formatted = formatter(value.text)
                prediction = WeatherPrediction(name, formatted)
                hour_forecast.predictions.append(prediction)
                i += 1

        for hour_forecast in hourly_forecasts:
            assert len(hour_forecast.predictions) == len(DIMS)

        # group into daily forecasts
        daily: dict[datetime.date, DailyForecast] = {}
        for hour_forecast in hourly_forecasts:
            date = hour_forecast.forecast_hour.date()
            if date not in daily:
                daily[date] = DailyForecast(date)

            daily[date].hourly.append(hour_forecast)

        return list(daily.values())
