import argparse
import base64
import http
import json
import sys
import traceback
import typing
import urllib.error
import urllib.parse
import urllib.request
import urllib.response

from nacl import encoding, public

REPO_SECRET_ENPHASE_ACCESS_TOKEN = "ENPHASE_ACCESS_TOKEN"
REPO_SECRET_ENPHASE_REFRESH_TOKEN = "ENPHASE_REFRESH_TOKEN"


def default_is_success(response: urllib.response.addinfourl) -> bool:
    return response.status is not None and response.status < 400


def make_request(
    url: str,
    /,
    method: str = "GET",
    headers: dict | None = None,
    data: bytes | None = None,
    is_success: typing.Callable[
        [urllib.response.addinfourl], bool
    ] = default_is_success,
):
    request = urllib.request.Request(url, method=method, data=data)
    if headers is not None:
        for key, value in headers.items():
            request.add_header(key, value)

    try:
        with urllib.request.urlopen(request) as response:
            assert is_success(response)

            response_body = response.read()
            response_parsed = json.loads(response_body.decode("utf-8"))
            return response_parsed
    except urllib.error.HTTPError as exc:
        try:
            error_response = exc.read()
            error_parsed = json.loads(error_response.decode("utf-8"))
            print(f"Failed ({exc.code} {exc.reason}): {error_parsed}")
        except Exception:
            formatted_traceback = "".join(traceback.format_exception(*sys.exc_info()))
            print(f"Failed: {formatted_traceback}")


class RepoPublicKey(typing.TypedDict):
    key: str
    key_id: str


class Github:
    _auth_token: str
    _repo_name: str
    _repo_owner: str

    def __init__(self, auth_token: str, repo_name: str, repo_owner: str) -> None:
        self._auth_token = auth_token
        self._repo_name = repo_name
        self._repo_owner = repo_owner

    def set_repo_secret(self, secret_name: str, secret_value: str) -> None:
        url = f"https://api.github.com/repos/{self._repo_owner}/{self._repo_name}/actions/secrets/{secret_name}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._auth_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        public_key = self._get_public_key()
        data = urllib.parse.urlencode(
            {
                "encrypted_value": self._encrypt(public_key["key"], secret_value),
                "key_id": public_key["key_id"],
            },
            quote_via=urllib.parse.quote,
        ).encode()

        def _is_success(response: urllib.response.addinfourl) -> bool:
            return response.status is not None and http.HTTPStatus(response.status) in (
                http.HTTPStatus.CREATED,
                http.HTTPStatus.NO_CONTENT,
            )

        make_request(
            url, method="PUT", headers=headers, data=data, is_success=_is_success
        )

    def _get_public_key(self) -> RepoPublicKey:
        url = f"https://api.github.com/repos/{self._repo_owner}/{self._repo_name}/actions/secrets/public-key"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._auth_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        response: RepoPublicKey = make_request(url, headers=headers)
        return response

    def _encrypt(self, public_key_str: str, secret_value: str) -> str:
        """Encrypt a Unicode string using the public key."""
        public_key = public.PublicKey(
            public_key_str.encode("utf-8"), encoding.Base64Encoder
        )
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")


class EnphaseAuthTokenResponse(typing.TypedDict):
    """
    See Section 10 in https://developer-v4.enphase.com/docs/quickstart.html

    There are other fields; these are the ones this script cares about.
    """

    access_token: str
    refresh_token: str


class Enphase:
    _client_id: str
    _client_secret: str

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def generate_new_tokens(self, refresh_token: str) -> EnphaseAuthTokenResponse:
        base_url = f"https://api.enphaseenergy.com/oauth/token"
        query_parameters = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        url = f"{base_url}?{urllib.parse.urlencode(query_parameters, quote_via=urllib.parse.quote)}"

        auth = f"{self._client_id}:{self._client_secret}".encode(encoding="utf-8")
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth).decode(encoding='utf-8')}"
        }
        response: EnphaseAuthTokenResponse = make_request(
            url, method="POST", headers=headers
        )
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--github_repo_name", type=str)
    parser.add_argument("--github_repo_owner", type=str)
    parser.add_argument(
        "--github_access_token",  # repo scoped
        type=str,
    )
    parser.add_argument(
        "--enphase_refresh_token",
        type=str,
    )
    parser.add_argument("--enphase_client_id", type=str)
    parser.add_argument("--enphase_client_secret", type=str)
    args = parser.parse_args()

    enphase_client = Enphase(args.enphase_client_id, args.enphase_client_secret)
    tokens = enphase_client.generate_new_tokens(args.enphase_refresh_token)

    github_client = Github(
        args.github_access_token, args.github_repo_name, args.github_repo_owner
    )
    github_client.set_repo_secret(
        REPO_SECRET_ENPHASE_ACCESS_TOKEN, tokens["access_token"]
    )
    github_client.set_repo_secret(
        REPO_SECRET_ENPHASE_REFRESH_TOKEN, tokens["refresh_token"]
    )
