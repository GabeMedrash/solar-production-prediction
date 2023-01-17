import csv
import datetime
import pathlib
import typing

X: typing.TypeAlias = list[float | int]
Y: typing.TypeAlias = float


def load_data(training_data: pathlib.Path) -> tuple[list[X], list[Y], list[str]]:
    x: list[X] = []
    y: list[Y] = []
    fieldnames: list[str] = []
    with open(training_data, mode="r", newline="") as fd:
        reader = csv.DictReader(fd)
        if not reader.fieldnames:
            raise ValueError(
                "Cannot parse fieldnames (and therefore field ordering) of training data"
            )
        fieldnames = list(reader.fieldnames)
        for row in reader:
            evidence: X = []
            for key in fieldnames:
                value = row[key]
                if key == "energy_production_Wh":
                    y.append(float(value))
                elif key == "date":
                    evidence.append(datetime.date.fromisoformat(value).month)
                else:
                    evidence.append(float(value))

            x.append(evidence)

    return (x, y, fieldnames)
