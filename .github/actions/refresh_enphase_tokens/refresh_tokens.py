import pathlib
import sys


def find_repo_root() -> pathlib.Path | None:
    ROOT_DIR_SIGNAL_FILE = "pyproject.toml"
    parents = pathlib.Path(__file__).parents
    for parent in parents:
        if (parent / ROOT_DIR_SIGNAL_FILE).exists():
            # Hit the root of the repo
            return parent
    return None


if __name__ == "__main__":
    root = find_repo_root()
    if root is None:
        raise EnvironmentError(
            "Expected script to run in a directory with a `pyproject.toml` file in its root"
        )
    sys.path.append(str(root))

    from src.solar_production_prediction.env import (
        Env,
    )
    from src.solar_production_prediction.weather_api.enphase import (
        Enphase,
    )

    env = Env()
    enphase_client = Enphase(env=env)
    tokens = enphase_client.generate_new_tokens()
    env.enphase_secret_tokens = tokens
