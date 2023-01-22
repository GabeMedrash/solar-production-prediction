import dataclasses
import datetime
import enum
import http
import typing
import urllib.error

from ..env import Env
from .http_client import HttpClient


class AQIParameter(enum.Enum):
    Ozone = "OZONE"
    PM2_5 = "PM2.5"


class HistoricalAQIRecordResponse(typing.TypedDict):
    ParameterName: str
    AQI: float


class AQIForecastRecordResponse(typing.TypedDict):
    DateForecast: str
    ParameterName: str
    AQI: float


@dataclasses.dataclass
class AQIDailyForecast:
    date: datetime.date
    aqi: float


class AirNowApi:
    """
    Client for https://docs.airnowapi.org/webservices
    """

    _env: Env
    _http_client: HttpClient

    def __init__(
        self, http_client: HttpClient = HttpClient(), env: Env = Env()
    ) -> None:
        self._env = env
        self._http_client = http_client

    def get_historical_aqi(self, date: datetime.date) -> typing.Optional[float]:
        lat, lon = self._env.latlong()
        response: list[HistoricalAQIRecordResponse] = self._http_client.get_json(
            f"https://www.airnowapi.org/aq/observation/latLong/historical/?format=application/json&latitude={lat}&longitude={lon}&date={date.isoformat()}T00-0000&distance=10&API_KEY={self._env.airnow_api_key()}",
            retry_wait=self._retry_waiter,
        )

        if not isinstance(response, list):
            return None

        for record in response:
            if record["ParameterName"] == AQIParameter.PM2_5.value:
                return float(record["AQI"])

        return None

    def get_forecast_aqi(self) -> list[AQIDailyForecast]:
        lat, lon = self._env.latlong()
        response: list[AQIForecastRecordResponse] = self._http_client.get_json(
            f"https://www.airnowapi.org/aq/forecast/latLong/?format=application/json&latitude={lat}&longitude={lon}&distance=10&API_KEY={self._env.airnow_api_key()}"
        )

        if not isinstance(response, list):
            return []

        daily_forecasts = []
        for forecast in response:
            if forecast["ParameterName"] == AQIParameter.PM2_5.value:
                date = datetime.date.fromisoformat(forecast["DateForecast"].strip())
                daily_forecast = AQIDailyForecast(date, float(forecast["AQI"]))
                daily_forecasts.append(daily_forecast)

        return daily_forecasts

    def _retry_waiter(self, exc: BaseException | None) -> float:
        if (
            isinstance(exc, urllib.error.HTTPError)
            and http.HTTPStatus(int(exc.code)) == http.HTTPStatus.TOO_MANY_REQUESTS
        ):
            return 60 * 60  # 60 seconds * 60 minutes == 1 hour

        return 2.0  # Any other transient error, just wait a couple seconds
