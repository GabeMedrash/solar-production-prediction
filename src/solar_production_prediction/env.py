import json
import os
import pathlib
import typing

import dotenv
import nacl.secret

dotenv.load_dotenv()


class EnphaseTokens(typing.TypedDict):
    ENPHASE_ACCESS_TOKEN: str
    ENPHASE_REFRESH_TOKEN: str


class Env:
    ENPHASE_SECRET_TOKENS_FILE = "enphase_tokens.secret"

    ENV_VAR_AIRNOW_API_KEY = "AIRNOW_API_KEY"
    ENV_VAR_ENPHASE_API_KEY = "ENPHASE_API_KEY"
    ENV_VAR_ENPHASE_CLIENT_ID = "ENPHASE_CLIENT_ID"
    ENV_VAR_ENPHASE_CLIENT_SECRET = "ENPHASE_CLIENT_SECRET"
    ENV_VAR_ENPHASE_SECRETS_FILE_ENCRYPTION_KEY = (
        "ENPHASE_SECRETS_FILE_ENCRYPTION_KEY_HEX"
    )
    ENV_VAR_ENPHASE_SYSTEM_ID = "ENPHASE_SYSTEM_ID"
    ENV_VAR_LAT = "LAT"
    ENV_VAR_LON = "LON"

    """
    Convenience wrapper for getting environment variables this application cares about.
    If any of these environment variables are not present, fail.

    Env vars are expected to be found in a `.env` file (gitignored) in the root of this repository.
    For testing, pass a dictionary into the constructor with the expected keys.
    """
    _env: dict[str, str]
    _enphase_secret_tokens: EnphaseTokens | None

    def __init__(
        self, environ: dict[str, str] = os.environ.copy(), enphase_tokens=None
    ) -> None:
        self._env = environ
        self._enphase_secret_tokens = enphase_tokens

    def airnow_api_key(self) -> str:
        return self._env[Env.ENV_VAR_AIRNOW_API_KEY]

    def enphase_api_key(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_API_KEY]

    def enphase_client_id(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_CLIENT_ID]

    def enphase_client_secret(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_CLIENT_SECRET]

    def enphase_access_token(self) -> str:
        return self.enphase_secret_tokens["ENPHASE_ACCESS_TOKEN"]

    def enphase_refresh_token(self) -> str:
        return self.enphase_secret_tokens["ENPHASE_REFRESH_TOKEN"]

    def enphase_system_id(self) -> str:
        return self._env[Env.ENV_VAR_ENPHASE_SYSTEM_ID]

    @property
    def enphase_secret_tokens(self) -> EnphaseTokens:
        if self._enphase_secret_tokens is None:
            secrets_file = self._find_enphase_secrets_file()
            if secrets_file is None:
                raise FileNotFoundError(f"Cannot find {Env.ENPHASE_SECRET_TOKENS_FILE}")

            box = nacl.secret.SecretBox(self._enphase_secrets_file_encryption_key())
            decrypted_secrets = box.decrypt(secrets_file.read_bytes())
            parsed: EnphaseTokens = json.loads(decrypted_secrets)
            self._enphase_secret_tokens = parsed
        return self._enphase_secret_tokens

    @enphase_secret_tokens.setter
    def enphase_secret_tokens(self, tokens: EnphaseTokens) -> None:
        secrets_file = self._find_enphase_secrets_file()
        if secrets_file is None:
            raise FileNotFoundError(f"Cannot find {Env.ENPHASE_SECRET_TOKENS_FILE}")

        box = nacl.secret.SecretBox(self._enphase_secrets_file_encryption_key())
        encrypted = box.encrypt(json.dumps(tokens).encode("utf-8"))
        secrets_file.write_bytes(encrypted)

    def latlong(self) -> tuple[float, float]:
        lat = float(self._env[Env.ENV_VAR_LAT])
        lon = float(self._env[Env.ENV_VAR_LON])
        return (lat, lon)

    def _enphase_secrets_file_encryption_key(self) -> bytes:
        hex_key = self._env[Env.ENV_VAR_ENPHASE_SECRETS_FILE_ENCRYPTION_KEY]
        return bytes.fromhex(hex_key)

    def _find_enphase_secrets_file(self) -> pathlib.Path | None:
        ROOT_DIR_SIGNAL_FILE = "pyproject.toml"
        parents = pathlib.Path(__file__).parents
        for parent in parents:
            expected = parent / Env.ENPHASE_SECRET_TOKENS_FILE
            if expected.exists():
                return expected

            if (parent / ROOT_DIR_SIGNAL_FILE).exists():
                # Hit the root of the repo and the secrets file doesn't exist
                return None
