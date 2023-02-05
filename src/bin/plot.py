"""
To run:
`$ venv/bin/python -m src.bin.plot`
"""
import dataclasses
import datetime
import pathlib
import textwrap

import duckdb
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from src.persistence import (
    PREDICTIONS_DB_PATH,
    PREDICTIONS_TBL,
)


db_con = duckdb.connect(PREDICTIONS_DB_PATH)
query = db_con.execute(
    textwrap.dedent(f"""\
        SELECT
            prediction_for_date,
            date_of_prediction,
            model_version,
            energy_production,
            actual_energy_production
        FROM
            {PREDICTIONS_TBL}
        WHERE
            actual_energy_production IS NOT NULL
            AND
            today() - prediction_for_date < 32;
    """),
)
rows: list[
    tuple[datetime.datetime, datetime.datetime, str, float, float]
] = query.fetchall()


@dataclasses.dataclass
class Forecast:
    forecast_distance: int  # number of days away this forecast was made
    model: str
    predicted_production: float


@dataclasses.dataclass
class GroupedForecasts:
    date: datetime.datetime
    actual_production: float
    predictions: list[Forecast] = dataclasses.field(default_factory=list)


max_predictions_made_for_date = 0
grouped: dict[datetime.datetime, GroupedForecasts] = {}
for row in rows:
    (
        prediction_for_date,
        date_of_prediction,
        model_version,
        predicted_production,
        actual_production,
    ) = row
    if prediction_for_date not in grouped:
        grouped[prediction_for_date] = GroupedForecasts(
            prediction_for_date, actual_production
        )

    grouped[prediction_for_date].predictions.append(
        Forecast(
            (prediction_for_date - date_of_prediction).days,
            model_version,
            predicted_production,
        )
    )
    max_predictions_made_for_date = max(
        max_predictions_made_for_date, len(grouped[prediction_for_date].predictions)
    )

fig, ax = plt.subplots()

for i in range(0, max_predictions_made_for_date):
    X = []
    Y = []
    for group in grouped.values():
        if i > len(group.predictions) - 1:
            continue
        forecast = group.predictions[i]
        X.append(group.date)
        Y.append(forecast.predicted_production)
    ax.scatter(
        X,
        Y,
        label=f"{forecast.forecast_distance} day prediction (model v{forecast.model})",
    )

X = []
Y = []
for group in grouped.values():
    X.append(group.date)
    Y.append(group.actual_production)
ax.scatter(X, Y, c="#000000", marker="*", label="Actual")


fig.autofmt_xdate()
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.set_xlabel("Date")
ax.set_ylabel("Wh")
fig.set(figwidth=20, figheight=10)  # inches
plt.legend(loc="upper left")

results_folder = pathlib.Path(__file__).parent.parent.parent / "results"
plt.savefig(results_folder / "plot.png", format="png")
