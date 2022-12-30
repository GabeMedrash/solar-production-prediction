import os


class Env:
    _env: dict[str, str]

    def __init__(self, environ: dict[str, str] = os.environ.copy()) -> None:
        self._env = environ

    def accuweather_api_key(self) -> str:
        return self._env["ACCUWEATHER_API_KEY"]

    def latlong(self) -> tuple[float, float]:
        lat = float(self._env["LAT"])
        lon = float(self._env["LON"])
        return (lat, lon)

    def openweather_api_key(self) -> str:
        return self._env["OPEN_WEATHER_API_KEY"]
