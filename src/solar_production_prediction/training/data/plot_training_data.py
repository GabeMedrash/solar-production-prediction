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


def read_data(dimension: str) -> tuple[XAxisData, YAxisData]:
    dates: XAxisData = []
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
            dim_data.append(get_field_and_format(dimension, float))

    return dates, dim_data


def plot_data(
    x_axis_data: XAxisData, y_axis_data: YAxisData, ylabel: str, title: str
) -> None:
    manager = plt.get_current_fig_manager()
    window_width, window_height = manager.window.maxsize()

    fig, ax = plt.subplots()
    ax.scatter(x_axis_data, y_axis_data)
    ax.set(
        xlabel="date",
        ylabel=ylabel,
        title=title,
    )
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.set(figwidth=window_width // 100, figheight=window_height // 100)
    ax.grid()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dimension",
        type=str,
    )
    parser.add_argument("--ylabel", dest="ylabel", type=str, required=False)
    parser.add_argument("--title", dest="title", type=str, required=False)
    args = parser.parse_args()

    x_axis_data, y_axis_data = read_data(args.dimension)

    ylabel = args.ylabel if args.ylabel else args.dimension
    title = args.title if args.title else f"{args.dimension.capitalize()} over time"

    plot_data(x_axis_data, y_axis_data, ylabel, title)
