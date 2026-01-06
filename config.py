import json
import os.path
from dataclasses import dataclass

from loguru import logger

SETTINGS_FILE_NAME = "settings.json"
DEFAULT_START_TIME = "09:00:00"
DEFAULT_END_TIME = "18:00:00"


try:
    with open(SETTINGS_FILE_NAME) as config_file:
        settings_dict = json.load(config_file)
except FileNotFoundError:
    logger.error("Settings file is not found. Please edit settings.json.")
    raise


@dataclass
class Config:
    incoming_data_file_path: str
    x_col_number: int
    y_col_number: int
    name_filter_criteria: str
    name_filter_col_num: int
    enable_name_filter: bool
    rows_limit_counter: int
    time_filter_enable: bool
    start_time: str
    end_time: str
    graph_color: str
    transparent_png: bool
    output_dir_name: str


@dataclass
class NameFilter:
    name_filter_criteria: str
    name_filter_col_num: int
    filter_enable: bool


@dataclass
class TimeFilter:
    start_time_value: str
    end_time_value: str
    filter_enable: bool


try:
    settings = Config(
        incoming_data_file_path=settings_dict["incoming_data_file_path"],
        x_col_number=settings_dict["x_col_number"],
        y_col_number=settings_dict["y_col_number"],
        name_filter_criteria=settings_dict.get("name_filter_criteria", ""),
        name_filter_col_num=settings_dict["name_filter_col_num"],
        enable_name_filter=settings_dict.get("enable_name_filter", True),
        rows_limit_counter=settings_dict.get("rows_limit_counter", 0),
        time_filter_enable=settings_dict.get("time_filter_enable", True),
        start_time=settings_dict.get("start_time", DEFAULT_START_TIME),
        end_time=settings_dict.get("end_time", DEFAULT_END_TIME),
        graph_color=settings_dict.get("graph_color", "black"),
        transparent_png=settings_dict.get("transparent_png", False),
        output_dir_name=settings_dict.get("output_dir_name", "output_data"),
    )
except KeyError:
    logger.error("Critical error. There is no critical value.")
    raise KeyError

try:
    if not os.path.exists(settings.incoming_data_file_path):
        logger.error("Incoming file does not exist.")
        raise ValueError("Incoming file does not exist.")
except ValueError:
    raise

try:
    if not os.path.exists(settings.output_dir_name):
        os.mkdir(settings.output_dir_name)
except Exception:
    logger.error(f"Can't create output directory {settings.output_dir_name}")
    raise

name_filter = NameFilter(
    name_filter_criteria=settings.name_filter_criteria,
    name_filter_col_num=settings.name_filter_col_num,
    filter_enable=settings.enable_name_filter,
)
time_filter = TimeFilter(
    start_time_value=settings.start_time,
    end_time_value=settings.end_time,
    filter_enable=settings.time_filter_enable,
)
