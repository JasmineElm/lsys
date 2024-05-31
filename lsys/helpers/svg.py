#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    SVG functions
"""

from helpers import utils


def dict_to_tags(tag_dict):
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

# Header and footer


def svg_header(paper_size, drawable_area):
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
    xml1 += "xmlns='http://www.w3.org/2000/svg' version='1.1'>"
    return xml1


def svg_footer():
    """return the SVG footer"""
    return "</svg>"


# # build SVG file


def svg_list_to_string(svg_list, mini=False):
    """convert a list of SVG lines to a string"""
    if mini:
        return "".join(svg_list)
    else:
        return "\n".join(svg_list)


def build_svg_file(paper_size, drawable_area, svg_list):
    """build the SVG file from the following parts:
    header
    svg_list
    footer
    """
    # if svg_list is empty, break with warning
    if not svg_list:
        print("svg_list is empty, you'll probably have a broken SVG...")
        return
    svg_list.insert(0, svg_header(paper_size, drawable_area))
    svg_list.append(svg_footer())
    return svg_list


def write_file(filename, svg_list, mini=False):
    """Write the SVG file"""
    # calculate size of output file
    # if svg_list is empty, break with warning
    if not svg_list:
        print("svg_list is empty, you'll probably have a broken SVG...")
        return
    utils.calc_output_size(svg_list)
    with open(filename, "w", encoding="utf-8") as svg_file:
        # make sure svg_list is a list of strings
        if not isinstance(svg_list[0], str):
            print("svg_list is empty")
            return
        if not isinstance(svg_list[0], str):
            print("svg_list is not a list of strings")
            return
        for line in svg_list:
            if mini:
                svg_file.write(line)
            else:
                svg_file.write(line + "\n")


def set_comment(comment_dict):
    """add a comment to the SVG file"""
    comment_string = "<!--\n"
    for key, value in comment_dict.items():
        if key == "RULES":
            value = str(value)
            value = value.replace("--", "- -").replace("--", "+ - -")
        comment_string += f"{key}: {value}\n"
    comment_string += "-->"
    return comment_string




