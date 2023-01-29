import base64
import datetime
import http
import random
import typing
import urllib.error
import urllib.parse

from ..env import EnphaseTokens, Env
from .http_client import HttpClient


class EnphaseProductionSummary(typing.TypedDict):
    """Docs: https://developer-v4.enphase.com/docs.html"""

    production: list[int]


class EnphaseAuthTokenResponse(typing.TypedDict):
    """
    See Section 10 in https://developer-v4.enphase.com/docs/quickstart.html

    There are other fields; these are the ones this script cares about.
    """

    access_token: str
    refresh_token: str


class Enphase:
    """
    Client for Enphase Developer API.
    Docs: https://developer-v4.enphase.com/docs/quickstart.html
    """

    _env: Env
    _http_client: HttpClient

    def __init__(
        self, http_client: HttpClient = HttpClient(), env: Env = Env()
    ) -> None:
        self._env = env
        self._http_client = http_client

    def energy_produced_on_date(self, date: datetime.date) -> int:
        base_url = f"https://api.enphaseenergy.com/api/v4/systems/{self._env.enphase_system_id()}/energy_lifetime"
        query_parameters = {
            "key": self._env.enphase_api_key(),
            "start_date": date.isoformat(),
            "end_date": date.isoformat(),
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_parameters, quote_via=urllib.parse.quote)}"
        headers = {"Authorization": f"Bearer {self._env.enphase_access_token()}"}
        response: EnphaseProductionSummary = self._http_client.get_json(
            url, headers=headers, retry_wait=self._retry_waiter
        )
        assert len(response["production"]) == 1
        return response["production"][0]

    def generate_new_tokens(self) -> EnphaseTokens:
        base_url = f"https://api.enphaseenergy.com/oauth/token"
        query_parameters = {
            "grant_type": "refresh_token",
            "refresh_token": self._env.enphase_refresh_token(),
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_parameters, quote_via=urllib.parse.quote)}"

        auth = f"{self._env.enphase_client_id()}:{self._env.enphase_client_secret()}".encode(
            encoding="utf-8"
        )
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth).decode(encoding='utf-8')}"
        }
        response: EnphaseAuthTokenResponse = self._http_client.get_json(
            url, method="POST", headers=headers
        )
        tokens: EnphaseTokens = {
            "ENPHASE_ACCESS_TOKEN": response["access_token"],
            "ENPHASE_REFRESH_TOKEN": response["refresh_token"],
        }
        return tokens

    def _retry_waiter(self, exc: BaseException | None) -> float:
        if (
            isinstance(exc, urllib.error.HTTPError)
            and http.HTTPStatus(int(exc.code)) == http.HTTPStatus.TOO_MANY_REQUESTS
        ):
            return 60.0  # 60 seconds

        return random.randrange(
            2, 5
        )  # Any other transient error, just wait a few seconds
