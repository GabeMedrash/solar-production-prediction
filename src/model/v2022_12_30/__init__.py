import pathlib
import pickle

from ..model_base import Model

PERSISTED_MODEL = pathlib.Path(__file__).parent / "model.pickle"

model: Model | None = None
try:
    with open(PERSISTED_MODEL, "rb") as file_handle:
        model = pickle.load(file_handle)
except FileNotFoundError:
    print(f"Model {PERSISTED_MODEL} does not exist; model must be trained.")

__all__ = ("model", "PERSISTED_MODEL")
