from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

from config import (
    DEFAULT_END_TIME,
    DEFAULT_START_TIME,
    NameFilter,
    name_filter,
    settings,
    time_filter,
)


def read_large_file(file_path: str):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()


def start_time_filter(
    current_time_value: datetime, limit_time_value: str = DEFAULT_START_TIME
):
    if current_time_value < datetime.strptime(limit_time_value, "%H:%M:%S"):
        return True
    return False


def end_time_filter(
    current_time_value: datetime, limit_time_value: str = DEFAULT_END_TIME
):
    if current_time_value > datetime.strptime(limit_time_value, "%H:%M:%S"):
        return True
    return False


def get_coordinates_from_csv(
    file: str, x: int, y: int, limit_rows: int = settings.rows_limit_counter
) -> list:
    coordinates_list = []
    counter = 0

    for row in read_large_file(file):
        if limit_rows and counter > limit_rows:
            break

        incoming_data = row.strip().split(";")

        if len(incoming_data) > 1:
            if (
                name_filter.filter_enable
                and incoming_data[name_filter.name_filter_col_num]
                != name_filter.name_filter_criteria
            ):
                continue
            try:
                y_coord = float("".join(str.split(incoming_data[y])))
                x_coord = datetime.strptime(f"{incoming_data[x]}", "%H:%M:%S")
            except ValueError:
                continue
            if time_filter.filter_enable and start_time_filter(
                x_coord, time_filter.start_time_value
            ):
                continue
            if time_filter.filter_enable and end_time_filter(
                x_coord, time_filter.end_time_value
            ):
                continue
            if limit_rows:
                counter += 1
            coordinates_list.append([x_coord, y_coord])

    if name_filter.filter_enable:
        logger.debug("Name filter is enabled. Submitting coordinates with name filter applied.")
    return coordinates_list


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
        title_line = file.readline().strip().split(";")

    time_formatter = mdates.DateFormatter("%H-%M-%S")
    plt.rcParams.update({"font.size": 8})

    plt.plot(x_coord_list, y_coord_list, color=settings.graph_color)
    plt.gcf().set_size_inches(15, 5)
    plt.gca().xaxis.set_major_formatter(time_formatter)
    plt.title(f"Graph {name_filter.name_filter_criteria}")
    plt.xlabel(title_line[settings.x_col_number])
    plt.ylabel(title_line[settings.y_col_number])
    plt.grid()

    min_y_value = np.min(y_coord_list)
    min_y_index = np.argmin(y_coord_list)
    plt.scatter(
        x_coord_list[min_y_index],
        min_y_value,
        color="cyan",
        label=f"Min: {min_y_value}/{datetime.strftime(x_coord_list[min_y_index], '%H:%M:%S')}",
    )
    plt.legend()

    max_y_value = np.max(y_coord_list)
    max_y_index = np.argmax(y_coord_list)
    plt.scatter(
        x_coord_list[max_y_index],
        max_y_value,
        color="orange",
        label=f"Max: {max_y_value}/{datetime.strftime(x_coord_list[max_y_index], '%H:%M:%S')}",
    )
    plt.legend()

    plt.savefig(
        f"output_data/{name_filter.name_filter_criteria}.png",
        format="png",
        dpi=600,
        transparent=settings.transparent_png,
    )
    plt.show()
