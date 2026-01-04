import os.path
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from config import TimeCondition, logger, name_filter, settings, time_filter


def read_large_file(file_path: str):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()


def checking_time_filter_condition(
    current_time_value: datetime,
    limit_time_value: str,
    condition: TimeCondition = TimeCondition.START_TIME,
) -> bool:
    if condition == TimeCondition.START_TIME:
        if current_time_value < datetime.strptime(
            limit_time_value, "%H:%M:%S"
        ):
            return True
    elif condition == TimeCondition.END_TIME:
        if current_time_value > datetime.strptime(
            limit_time_value, "%H:%M:%S"
        ):
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

        incoming_data = row.strip().split(settings.separator)

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
            if time_filter.filter_enable and checking_time_filter_condition(
                x_coord, time_filter.start_time_value, TimeCondition.START_TIME
            ):
                continue
            if time_filter.filter_enable and checking_time_filter_condition(
                x_coord, time_filter.end_time_value, TimeCondition.END_TIME
            ):
                continue
            if limit_rows:
                counter += 1
            coordinates_list.append([x_coord, y_coord])

    if name_filter.filter_enable:
        logger.debug(
            "Name filter is enabled. Submitting coordinates with name filter applied."
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
        label=f"Min: {min_y_value}/{time_of_min}",
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
        label=f"Max: {max_y_value}/{time_of_max}",
    )
    plt.legend()


def plot_drawing(
    x_coord_list: list, y_coord_list: list, title_line: list
) -> None:
    time_formatter = mdates.DateFormatter("%H-%M-%S")
    graph_name = "Default named graph"
    if name_filter.filter_enable:
        graph_name = name_filter.name_filter_criteria
    plt.rcParams.update({"font.size": 8})

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

    plot_drawing(x_coord_list, y_coord_list, title_line)
