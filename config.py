import json
from dataclasses import dataclass

settings_file_name = "settings.json"

with open(settings_file_name) as config_file:
    settings_dict = json.load(config_file)


class Config:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)


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


DEFAULT_START_TIME = "09:00:00"
DEFAULT_END_TIME = "18:00:00"

settings = Config(settings_dict)
name_filter = NameFilter(
    name_filter_criteria=settings.name_filter_criteria,
    name_filter_col_num=settings.name_filter_col_num,
    filter_enable=settings.enamble_name_filter,
)

time_filter = TimeFilter(
    start_time_value=settings.start_time,
    end_time_value=settings.end_time,
    filter_enable=settings.time_filter_enable,
)
