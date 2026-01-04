import os.path
from datetime import datetime

import dateutil.parser
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from config import logger, name_filter, settings, time_filter

logger.add("error.log", level="ERROR", rotation="10 MB")

def read_large_file(file_path: str):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()


def get_coordinates_from_csv(
    file: str, x: int, y: int, limit_rows: int = settings.rows_limit_counter
) -> list:
    coordinates_list = []
    counter = 0

    for row in read_large_file(file):
        if limit_rows and counter > limit_rows:
            break

        incoming_data = row.strip().split(settings.separator)

        if len(incoming_data) > 1:
            if (
                name_filter.filter_enable
                and incoming_data[name_filter.name_filter_col_num]
                != name_filter.name_filter_criteria
            ):
                logger.debug("Skip incorrect row in file. Can't split that.")
                continue
            if counter == 0:
                counter += 1
                logger.debug("Skip first line in csv file.")
                continue
            try:
                y_coord = float("".join(str.split(incoming_data[y])))
                x_coord = dateutil.parser.parse(incoming_data[x])
            except ValueError:
                logger.warning("Value conversion error, please check format.")
                continue
            if time_filter.filter_enable and dateutil.parser.parse(
                time_filter.start_time_value
            ) < x_coord > dateutil.parser.parse(time_filter.end_time_value):
                continue

            counter += 1
            coordinates_list.append([x_coord, y_coord])

    if name_filter.filter_enable:
        logger.debug(
            f"Name filter is enabled. Submitting coordinates"
            f"with name filter applied."
        )
    return coordinates_list


def minimal_dot_drawing(x_coord_list: list, y_coord_list: list) -> None:
    min_y_value = np.min(y_coord_list)
    min_y_index = np.argmin(y_coord_list)
    time_of_min = datetime.strftime(x_coord_list[min_y_index], "%H:%M:%S")
    plt.scatter(
        x_coord_list[min_y_index],
        min_y_value,
        color="cyan",
        label=f"Min: {min_y_value} / {time_of_min}",
    )
    plt.legend()


def maximal_dot_drawing(x_coord_list: list, y_coord_list: list) -> None:
    max_y_value = np.max(y_coord_list)
    max_y_index = np.argmax(y_coord_list)
    time_of_max = datetime.strftime(x_coord_list[max_y_index], "%H:%M:%S")
    plt.scatter(
        x_coord_list[max_y_index],
        max_y_value,
        color="orange",
        label=f"Max: {max_y_value} / {time_of_max}",
    )
    plt.legend()


def plot_drawing(
    x_coord_list: list, y_coord_list: list, title_line: list
) -> None:
    time_formatter = mdates.DateFormatter("%H-%M-%S")
    graph_name = "Default named graph"

    if not all([len(x_coord_list), len(y_coord_list)]):
        logger.error("Array with incoming data is empty.")
        raise ValueError("Array with incoming data is empty.")

    if name_filter.filter_enable:
        graph_name = name_filter.name_filter_criteria

    plt.rcParams.update({"font.size": 8})
    plt.rcParams.update({"agg.path.chunksize": 10000})

    plt.plot(x_coord_list, y_coord_list, color=settings.graph_color)
    plt.gcf().set_size_inches(15, 5)
    plt.gca().xaxis.set_major_formatter(time_formatter)
    plt.title(graph_name)
    plt.xlabel(title_line[settings.x_col_number])
    plt.ylabel(title_line[settings.y_col_number])
    plt.grid()

    minimal_dot_drawing(x_coord_list, y_coord_list)
    maximal_dot_drawing(x_coord_list, y_coord_list)

    plt.savefig(
        os.path.join(settings.output_dir_name, f"{graph_name}.png"),
        format="png",
        dpi=600,
        transparent=settings.transparent_png,
    )
    plt.show()


if __name__ == "__main__":
    x_coord_list = []
    y_coord_list = []

    for x_coord, y_coord in get_coordinates_from_csv(
        settings.incoming_data_file_path,
        settings.x_col_number,
        settings.y_col_number,
    ):
        x_coord_list.append(x_coord)
        y_coord_list.append(y_coord)

    with open(settings.incoming_data_file_path, "r") as file:
        title_line = file.readline().strip().split(settings.separator)
    try:
        plot_drawing(x_coord_list, y_coord_list, title_line)
    except Exception:
        logger.error("Value error when trying to draw a graph.")
