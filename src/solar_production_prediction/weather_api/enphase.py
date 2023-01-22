import base64
import datetime
import time
import typing
import urllib.parse

from ..env import Env
from .http_client import HttpClient


PST = -datetime.timedelta(hours=8)
PDT = -datetime.timedelta(hours=7)


class EnphaseSystemSummary(typing.TypedDict):
    """ Docs: https://developer-v4.enphase.com/docs.html """
    energy_today: int  # in Wh
    last_report_at: int
    status: str
    summary_date: str  # in ISO format


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

    def energy_produced_today(self) -> int:
        base_url = f"https://api.enphaseenergy.com/api/v4/systems/{self._env.enphase_system_id()}/summary"
        query_parameters = {
            "key": self._env.enphase_api_key()
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_parameters, quote_via=urllib.parse.quote)}"
        headers = {
            "Authorization": f"Bearer {self._env.enphase_access_token()}"
        }
        response: EnphaseSystemSummary = self._http_client.get_json(url, headers=headers)

        # make sure this summary is for today and the system last submit a report today
        seattle_tz = PDT if time.localtime().tm_isdst != 0 else PST
        today = datetime.datetime.now(tz=datetime.timezone(seattle_tz)).date()
        assert today == datetime.date.fromisoformat(response["summary_date"])
        assert today == datetime.datetime.fromtimestamp(response["last_report_at"]).date()

        # TODO, check the status?
        return response["energy_today"]

    def generate_new_tokens(self, refresh_token: str) -> EnphaseAuthTokenResponse:
        base_url = f"https://api.enphaseenergy.com/oauth/token"
        query_parameters = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_parameters, quote_via=urllib.parse.quote)}"

        auth = f"{self._env.enphase_client_id()}:{self._env.enphase_client_secret()}".encode(encoding="utf-8")
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth).decode(encoding='utf-8')}"
        }
        response: EnphaseAuthTokenResponse = self._http_client(
            url, method="POST", headers=headers
        )
        return response
