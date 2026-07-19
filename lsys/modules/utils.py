#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General utility functions
"""

import os
import datetime
from pathlib import Path
from typing import Any


def create_dir(dir_path: Path | str) -> Path | str:
    """
    Creates a directory at the specified path if it does not already exist.

    Args:
        dir_path (str): The path of the directory to create.

    Returns:
        str: The path of the created directory.
    """
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def print_params(param_dict: dict[str, Any]) -> None:
    """print the parameters"""
    if "TITLE" in param_dict:
        # work out length of name
        title = f"--- {param_dict['TITLE']} "
        # print --- name  +  --- (68 - name_length) times
        print(f"{title}{(68 - len(title)) * '-'}\n")
    else:
        print(f"{68 * '-'}\n")
    for key, value in param_dict.items():
        if key == "TITLE":
            continue
        print(f"{key}: {value}")
    print(f"\n{68 * '-'}")


def calc_output_size(doc: list[str]) -> str:
    """sum character counts in doc to get output size"""
    length = 0
    for element in doc:
        length += len(element)
    return human_values(length)


def human_values(integer: int | float) -> str:
    """return a human readable value"""
    bold = "\033[1m"
    red = "\033[91m"
    amber = "\033[93m"
    green = "\033[92m"
    normal = "\033[0m"
    fs = "File size: "
    formats = [
        (10000000, f"{bold}{red}{fs}{{:.2f}}M{normal}", 1000000),
        (1000000, f"{bold}{amber}{fs}{{:.2f}}M{normal}", 1000000),
        (1000, f"{bold}{green}{fs}{{:.2f}}k{normal}", 1000),
        (-1, f"{bold}{green}{fs}{{:.0f}}b{normal}", 1),
    ]

    for threshold, format_str, divisor in formats:
        if integer > threshold:
            outstr = format_str.format(integer / divisor)
            break
    else:
        outstr = str(integer)
    print(outstr)
    return outstr


def date_string() -> str:
    """return the current date as a string"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def set_precision(value: float, precision: int) -> float | int:
    """set the precision of a value"""
    if precision <= 0:
        return int(round(value))
    return round(value, precision)


def string_to_dict(string_val: str) -> dict[str, Any]:
    """
    Converts a string into a dictionary.
    Parses formats like 'key:value,key2:value2' or 'key=value'.
    If no recognizable delimiters are found, returns {'str': string_val}.
    """
    if not string_val:
        return {}
        
    result = {}
    if ":" in string_val or "=" in string_val or "→" in string_val:
        pairs = string_val.split(",")
        for pair in pairs:
            if ":" in pair:
                k, v = pair.split(":", 1)
                result[k.strip().strip("\"'")] = v.strip().strip("\"'")
            elif "=" in pair:
                k, v = pair.split("=", 1)
                result[k.strip().strip("\"'")] = v.strip().strip("\"'")
            elif "→" in pair:
                k, v = pair.split("→", 1)
                result[k.strip().strip("\"'")] = v.strip().strip("\"'")
            else:
                p = pair.strip().strip("\"'")
                result[p] = p
        return result
        
    return {"str": string_val.strip("\"'")}
