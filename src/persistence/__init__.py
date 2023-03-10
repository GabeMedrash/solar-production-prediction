"""
[DuckDb](https://duckdb.org/docs/api/python/overview) is used as a persistence layer.
To play around with the database:
```
$ ./venv/bin/python
>>> import duckdb
>>> con = duckdb.connect("./src/persistence/predictions.duckdb")
>>> t = con.table("predictions")
>>> t.count()
>>> t.fetchall()
```
"""

import pathlib

from .ddl import PREDICTIONS_TBL

PREDICTIONS_DB_PATH = str(pathlib.Path(__file__).parent / "predictions.duckdb")

__all__ = ("PREDICTIONS_DB_PATH", "PREDICTIONS_TBL")
