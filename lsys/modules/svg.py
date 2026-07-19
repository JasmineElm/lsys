#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SVG functions
"""

import sys
from collections.abc import Mapping, Sequence
from typing import Any
from pathlib import Path
from modules import utils


def dict_to_tags(tag_dict: str | Mapping[str, object]) -> str:
    """convert a dict to a string of tags"""
    # if dict is empty, break with warning
    # if type is string, return it
    if isinstance(tag_dict, str):
        print("tag_dict is a string, returning it...")
        return tag_dict
    if not tag_dict:
        print("tag_dict is empty, you'll probably have a broken SVG...")
        return ""
    return " ".join([f"{key}='{value}'" for key, value in tag_dict.items()])


def svg_header(
    paper_size: Sequence[float | int],
    drawable_area: Sequence[float | int],
    background: str = "white",
) -> str:
    """
    Returns an SVG header string with the specified paper and canvas sizes.

    Args:
        paper_size (tuple): the width and height of the paper.
        canvas_size (tuple): the width and height of the canvas.

    Returns:
        str: An SVG header string with the specified paper and canvas sizes.
    """
    xml1 = "<?xml version='1.0' encoding='UTF-8' standalone='no'?>\n"
    xml1 += f"<svg width='{paper_size[0]}' height='{paper_size[1]}' "
    xml1 += f"viewBox='{drawable_area[0]} {drawable_area[1]} "
    xml1 += f"{drawable_area[2]} {drawable_area[3]}' "
    xml1 += f"style='background-color: {background};' "
    xml1 += "xmlns='http://www.w3.org/2000/svg' version='1.1'>"
    return xml1


def svg_footer() -> str:
    """return the SVG footer"""
    return "</svg>"


# # build SVG file


def build_svg_file(paper_size: Sequence[float | int], drawable_area: Sequence[float | int], svg_list: list[str], background: str = "white") -> list[str] | None:
    """build the SVG file from the following parts:
    header
    svg_list
    footer
    """
    # if svg_list is empty, break with warning
    if not svg_list:
        print("svg_list is empty, you'll probably have a broken SVG...")
        return
    svg_list.insert(0, svg_header(paper_size, drawable_area, background=background))
    svg_list.append(svg_footer())
    return svg_list


def write_file(filename: str | Path, svg_list: list[str] | None, mini: bool = False) -> None:
    """Write the SVG file"""
    # calculate size of output file
    # if svg_list is empty, break with warning
    if not svg_list:
        print("svg_list is empty, you'll probably have a broken SVG...")
        return
    utils.calc_output_size(svg_list)
    with open(filename, "w", encoding="utf-8") as svg_file:
        for line in svg_list:
            if mini:
                svg_file.write(line)
            else:
                svg_file.write(line + "\n")


def set_comment(comment_dict: dict[str, Any]) -> str:
    """add a comment to the SVG file"""
    comment_string = "<!--\n"
    for key, value in comment_dict.items():
        if key == "RULES":
            value = str(value)
            value = value.replace("--", "- -").replace("--", "+ - -")
        comment_string += f"{key}: {value}\n"
    comment_string += "-->"
    return comment_string


def scale_to_fit(object_list: list[tuple[tuple[float, float], tuple[float, float], float]], target_size: Sequence[float | int], bleed: float) -> list[tuple[tuple[float, float], tuple[float, float], float]]:
    """
    Scale and center a list of line coordinates to fit exactly within
    target_size (width, height) minus bleed on all sides, maintaining aspect ratio.
    """
    if not object_list:
        sys.exit("Object list is empty")

    xs = [coord[0] for obj in object_list for coord in (obj[0], obj[1])]
    ys = [coord[1] for obj in object_list for coord in (obj[0], obj[1])]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x
    height = max_y - min_y
    if width == 0:
        width = 1
    if height == 0:
        height = 1

    target_width = target_size[0] - 2 * bleed
    target_height = target_size[1] - 2 * bleed

    # Calculate uniform scaling factor to fit inside the target area
    scale = min(target_width / width, target_height / height)

    # Calculate the new centered offset
    scaled_width = width * scale
    scaled_height = height * scale

    x_offset = bleed + (target_width - scaled_width) / 2.0 - (min_x * scale)
    y_offset = bleed + (target_height - scaled_height) / 2.0 - (min_y * scale)

    new_object_list = [
        (
            (obj[0][0] * scale + x_offset, obj[0][1] * scale + y_offset),
            (obj[1][0] * scale + x_offset, obj[1][1] * scale + y_offset),
            obj[2] if len(obj) > 2 else 1.0
        )
        for obj in object_list
    ]
    return new_object_list


def line(
    start_xy: tuple[float, float], end_xy: tuple[float, float], addnl_styles: dict[str, Any] | None = None
) -> str:
    """return a line from start_xy to end_xy"""
    styles = f" {dict_to_tags(addnl_styles)}" if addnl_styles else ""
    return f"<line x1='{start_xy[0]}' y1='{start_xy[1]}' x2='{end_xy[0]}' y2='{end_xy[1]}'{styles} />"

def path(points: list[tuple[float, float]], addnl_styles: dict[str, Any] | None = None) -> str:
    """return a path from a list of points"""
    if not points:
        return ""
    styles = f" {dict_to_tags(addnl_styles)}" if addnl_styles else ""
    d = f"M {points[0][0]} {points[0][1]} " + " ".join([f"L {p[0]} {p[1]}" for p in points[1:]])
    return f"<path d='{d}'{styles} />"
