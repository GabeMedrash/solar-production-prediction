"""
Train model and print summary

To run:
`./venv/bin/python -m src.model.v2022_12_30`
"""
import datetime
import pathlib
import pickle
import stat

from . import PERSISTED_MODEL
from ..data import TRAINING_DATA, load_data
from .train import train

if PERSISTED_MODEL.exists():
    raise FileExistsError(
        "Model already trained. Create a new model instead of overwritting an existing one."
    )

# Create snapshot of training data from `data` module if it doesn't already exist
SNAPSHOT_TRAINING_DATA = pathlib.Path(__file__).parent / "training_data.csv"
if not SNAPSHOT_TRAINING_DATA.exists():
    SNAPSHOT_TRAINING_DATA.touch()
    SNAPSHOT_TRAINING_DATA.write_bytes(TRAINING_DATA.read_bytes())
    # set to readonly
    SNAPSHOT_TRAINING_DATA.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

x, y, fieldnames = load_data(SNAPSHOT_TRAINING_DATA)
model = train(x, y, fieldnames)

readme = f"""\
{datetime.date.today().isoformat()}
======
```json
{model.to_json()}
```
"""

README = pathlib.Path(__file__).parent / "README.md"
README.write_text(readme)

with open(PERSISTED_MODEL, "wb") as file_handle:
    pickle.dump(model, file_handle)
