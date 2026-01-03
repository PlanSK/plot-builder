from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

INCOMING_DATA_FILE = "incoming_data/20251225_Si_Cn_Br.csv"  # data file name
X_COL_NUMBER = 0  # col number of x coordinate
Y_COL_NUMBER = 7  # col number of y coordinate
FILTER_NAME = "SiH6"  # name for filter
FILTER_COL_NUM = 1  # col number with filter name
LIMIT_COUNTER = 0  # limit of rows
START_TIME_FILTER_ENABLE = True
DEFAULT_START_TIME = "09:00:00"
END_TIME_FILTER_ENABLE = True
DEFAULT_END_TIME = "18:00:00"
GRAPH_COLOR = "red"
FILTER_LIST = [FILTER_NAME, FILTER_COL_NUM]
TRANSPARENT_PNG = False


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
    file: str, x: int, y: int, filter: list = None, limit_rows: int = 0
) -> list:
    coordinates_list = []
    counter = 0
    for row in read_large_file(file):
        if limit_rows and counter > limit_rows:
            break

        incoming_data = row.strip().split(";")

        if len(incoming_data) > 1:
            if filter and incoming_data[filter[1]] != filter[0]:
                continue
            try:
                y_coord = float("".join(str.split(incoming_data[y])))
                x_coord = datetime.strptime(f"{incoming_data[x]}", "%H:%M:%S")
            except ValueError:
                continue
            if START_TIME_FILTER_ENABLE and start_time_filter(x_coord):
                continue
            if END_TIME_FILTER_ENABLE and end_time_filter(x_coord):
                continue
            if limit_rows:
                counter += 1
                # logger.debug(f"counter: {counter}/{limit_rows}")
            coordinates_list.append([x_coord, y_coord])

    if filter:
        logger.debug("coordinates with applied filter.")
    return coordinates_list


if __name__ == "__main__":
    x_coord_list = []
    y_coord_list = []
    for x_coord, y_coord in get_coordinates_from_csv(
        INCOMING_DATA_FILE,
        X_COL_NUMBER,
        Y_COL_NUMBER,
        FILTER_LIST,
        LIMIT_COUNTER,
    ):
        x_coord_list.append(x_coord)
        y_coord_list.append(y_coord)

    # logger.debug(x_coord_list)
    # logger.debug(y_coord_list)

    with open(INCOMING_DATA_FILE, "r") as file:
        title_line = file.readline().strip().split(";")

    time_formatter = mdates.DateFormatter("%H-%M-%S")
    plt.rcParams.update({"font.size": 8})
    plt.plot(x_coord_list, y_coord_list, color=GRAPH_COLOR)
    plt.gcf().set_size_inches(15, 5)
    plt.gca().xaxis.set_major_formatter(time_formatter)
    plt.title(f"Graph {FILTER_NAME}")
    plt.xlabel(title_line[X_COL_NUMBER])
    plt.ylabel(title_line[Y_COL_NUMBER])

    min_y_value = np.min(y_coord_list)
    min_y_index = np.argmin(y_coord_list)
    plt.scatter(x_coord_list[min_y_index], min_y_value, color="cyan", label=f"Min: {min_y_value}/{datetime.strftime(x_coord_list[min_y_index], '%H:%M:%S')}")
    plt.legend()
    max_y_value = np.max(y_coord_list)
    max_y_index = np.argmax(y_coord_list)
    plt.scatter(x_coord_list[max_y_index], max_y_value, color="orange", label=f"Max: {max_y_value}/{datetime.strftime(x_coord_list[max_y_index], '%H:%M:%S')}")
    plt.legend()

    plt.grid()
    plt.savefig(
        f"output_data/{FILTER_NAME}.png",
        format="png",
        dpi=600,
        transparent=TRANSPARENT_PNG,
    )
    plt.show()
