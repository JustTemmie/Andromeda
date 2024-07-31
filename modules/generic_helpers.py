import os
import random
import math
import re

if __name__ == "__main__":
    import sys
    sys.path.append(".")


def getProgressBar(current, max, width = 20):
    percent = int(width * current / max)
    bar = "█" * percent + "░" * (width - percent)

    return bar


def format_time(seconds):
    time_table = {
        "decade": seconds // 315576000,
        "year": seconds // 31557600 % 10,
        "day": seconds // 86400 % 365.25,
        "hour": seconds // 3600 % 24,
        "minute": seconds // 60 % 60,
        "second": seconds % 60,
    }
    
    return_string = ""
    
    for unit, value in time_table.items():
        value = math.floor(value)
        if value > 1:
            return_string += f"{value} {unit}s "
        elif value == 1:
            return_string += f"{value} {unit} "
    
    return return_string


# some regexes to remove comments and trailing commas
def json5_to_json(json5_str):
    json5_str = re.sub(r'//.*', '', json5_str)
    json5_str = re.sub(r'/\*.*?\*/', '', json5_str, flags=re.DOTALL)
    
    json5_str = re.sub(r',\s*([}\]])', r'\1', json5_str)
    return json5_str
