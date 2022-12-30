import os

from dotenv import load_dotenv

load_dotenv()


class Env:
    ENV_VAR_ENPHASE_AUTH_CODE = "ENPHASE_AUTH_CODE"
    ENV_VAR_ENPHASE_API_KEY = "ENPHASE_API_KEY"
    ENV_VAR_ENPHASE_USER_ID = "ENPHASE_USER_ID"
    ENV_VAR_LAT = "LAT"
    ENV_VAR_LON = "LON"

    """
    Convenience wrapper for getting environment variables this application cares about.
    If any of these environment variables are not present, fail.

    Env vars are expected to be placed into a `.env` file in the root of this repository.
    For testing, one could alternately pass a dictionary into the constructor with the expected keys.
    """
    _env: dict[str, str]

    def __init__(self, environ: dict[str, str] = os.environ.copy()) -> None:
        self._env = environ

    def enphase_auth_code(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_AUTH_CODE]

    def enphase_api_key(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_API_KEY]

    def enphase_user_id(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_USER_ID]

    def latlong(self) -> tuple[float, float]:
        lat = float(self._env[Env.ENV_VAR_LAT])
        lon = float(self._env[Env.ENV_VAR_LON])
        return (lat, lon)
