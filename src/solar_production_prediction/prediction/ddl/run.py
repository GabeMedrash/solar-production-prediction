"""
Setup predictions-db. DDL statements must be idempotent.

To run:
`./venv/bin/python -m src.solar_production_prediction.prediction.ddl.run`
"""

import duckdb

from . import CREATE_PREDICTIONS_TABLE
from .. import PREDICTIONS_DB_PATH

statements = (CREATE_PREDICTIONS_TABLE,)

db_con = duckdb.connect(PREDICTIONS_DB_PATH)
for statement in statements:
    db_con.execute(statement)
