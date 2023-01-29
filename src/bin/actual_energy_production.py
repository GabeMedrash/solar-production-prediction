"""
To run:
`$ venv/bin/python -m src.bin.actual_energy_production`
"""
import datetime

import duckdb

from src.external_data import Enphase
from src.persistence import (
    PREDICTIONS_DB_PATH,
    PREDICTIONS_TBL,
)

today = datetime.date.today()
enphase_client = Enphase()
db_con = duckdb.connect(PREDICTIONS_DB_PATH)
query = db_con.execute(
    f"SELECT DISTINCT prediction_for_date FROM {PREDICTIONS_TBL} WHERE actual_energy_production IS NULL AND prediction_for_date < ?",
    [today],
)
dates: list[tuple[datetime.datetime]] = query.fetchall()
for (date,) in dates:
    print(f"Fetching actual energy production on {date}")
    energy_produced = enphase_client.energy_produced_on_date(date)
    print(f"\tProduced {energy_produced}Wh. Persisting...")
    db_con.execute(
        f"UPDATE {PREDICTIONS_TBL} SET actual_energy_production = ? WHERE prediction_for_date = ?",
        [energy_produced, date],
    )
    print("\tPersisted.")
