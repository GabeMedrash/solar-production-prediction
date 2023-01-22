import argparse
import csv
import datetime
import pathlib
import typing

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

DATA_DIR = pathlib.Path(__file__).parent
TRAINING_DATA = DATA_DIR / "preprocessed_training_data.csv"

XAxisData: typing.TypeAlias = list[datetime.date]
YAxisData: typing.TypeAlias = list[int | float]


def read_data(dimension: str) -> tuple[XAxisData, YAxisData, YAxisData]:
    dates: XAxisData = []
    energy_production: YAxisData = []
    dim_data: YAxisData = []
    with open(TRAINING_DATA, mode="r", newline="") as fd:
        csv_reader = csv.DictReader(fd)
        if csv_reader.fieldnames is None or dimension not in csv_reader.fieldnames:
            raise ValueError()

        for row in csv_reader:

            def get_field_and_format(field, formatter):
                return formatter(row[field])

            dates.append(
                get_field_and_format("date", lambda ds: datetime.date.fromisoformat(ds))
            )
            energy_production.append(
                get_field_and_format("energy_production_Wh", float)
            )
            dim_data.append(get_field_and_format(dimension, float))

    return dates, energy_production, dim_data


def plot_data(
    dates: XAxisData, energy_production: YAxisData, dim_data: YAxisData, ylabel: str
) -> None:
    fig, ax = plt.subplots(2, 1)

    ax[0].plot(dates, energy_production, "bo")
    ax[0].set(
        xlabel="Date",
        ylabel="Energy production",
        title="Energy production by date",
    )
    ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax[0].grid(True)

    ax[1].plot(dates, dim_data, "go")
    ax[1].set(
        xlabel="Date",
        ylabel=ylabel,
        title=f"{ylabel.capitalize()} by date",
    )
    ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax[1].grid(True)

    fig.autofmt_xdate()
    manager = plt.get_current_fig_manager()
    window_width, window_height = manager.window.maxsize()
    fig.set(figwidth=window_width // 100, figheight=window_height // 100)

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dimension",
        type=str,
    )
    args = parser.parse_args()

    dates, energy_production, dim_data = read_data(args.dimension)
    plot_data(dates, energy_production, dim_data, args.dimension)
