"""
Setup predictions-db. DDL statements must be idempotent.

To run:
`./venv/bin/python -m src.persistence.ddl.run`
"""

import duckdb

from . import (
    CREATE_PREDICTIONS_TABLE,
    SWAP_ACCURACY_FOR_ACTUAL_WATTAGE,
)
from .. import PREDICTIONS_DB_PATH

statements = (CREATE_PREDICTIONS_TABLE, SWAP_ACCURACY_FOR_ACTUAL_WATTAGE)

db_con = duckdb.connect(PREDICTIONS_DB_PATH)
for statement in statements:
    db_con.execute(statement)
