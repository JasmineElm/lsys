#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Skeleton file for new scripts
"""
import random
import toml

# local libraries from the helpers directory
from helpers import draw, lsys, svg, utils

# Load config file and set DEFAULT parameters
config = toml.load("config.toml")
DEFAULT = config["DEFAULT"]

DEFAULT.update(
    {
        "IMAGE_SIZE": [
            DEFAULT["PAPER_SIZE"][0] * DEFAULT["PPMM"],
            DEFAULT["PAPER_SIZE"][1] * DEFAULT["PPMM"],
        ]
    }
)
DEFAULT.update({"BLEED": DEFAULT["BLEED"] * DEFAULT["PPMM"]})

DEFAULT.update(
    {
        "FILENAME": utils.create_dir(DEFAULT["OUTPUT_DIR"])
        + utils.generate_filename()
    })
print(f"Default parameters: {DEFAULT}")


def generate_filename(rules_dict):
    """return a string which can be used as a filename"""
    # rules is a dictionary, expand it to a string
    # print the length of the dictionary
    print(f"Length of rules_dict: {len(rules_dict)}")
    rule_string = ""
    for key, value in rules_dict.items():
        print(f"{key}-->{value}")
        rule_string += f"{key}→{value},"
        # strip final comma, and return
    rule_string = rule_string.rstrip(",")
    return rule_string


def set_viewbox(object_list, bleed):
    """set the viewbox based a list of xy tuples"""
    # if  object list is empty, break
    if not object_list:
        print("Object list is empty")
        exit()
    xs = [coord[0] for obj in object_list for coord in obj]
    ys = [coord[1] for obj in object_list for coord in obj]
    min_x = min(xs)  # if min(xs) < 0 min_x = min(xs) - bleed
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    for param in [min_x, max_x, min_y, max_y]:
        if param < 0:
            param -= bleed
        else:
            param += bleed
    viewbox = (
        min_x // 1,
        min_y // 1,
        (1 + max_x - min_x) // 1,
        (1 + max_y - min_y) // 1,
    )
    return viewbox


def set_image_size(viewbox):
    """set the image size based on the viewbox"""
    return ((viewbox[2] - viewbox[0]), (viewbox[3] - viewbox[1]))


# function to translate a list of coordinates
# to have positive values


def set_precision(value, precision=3):
    """set the precision of a float"""
    return round(value, precision)


def translate_coords(object_list):
    """translate a list of coordinates to have positive values"""
    min_x = min(min(obj[i][0] for i in range(2)) for obj in object_list)
    min_y = min(min(obj[i][1] for i in range(2)) for obj in object_list)
    x_offset = abs(min_x)
    y_offset = abs(min_y)
    print(f"min_x: {min_x}, min_y: {min_y}")
    new_object_list = [
        (
            (obj[0][0] + x_offset, obj[0][1] + y_offset),
            (obj[1][0] + x_offset, obj[1][1] + y_offset),
        )
        for obj in object_list
    ]
    return new_object_list


def one_range_to_another(value, old_min, old_max, new_min, new_max):
    """convert a value from one range to another"""
    return ((value - old_min) * (new_max - new_min) /
            (old_max - old_min) + new_min)


def resize_coords(object_list, max_xy, min_xy):
    """simple min/max resize of a list of coordinates

    Args:
        object_list (list): list of coordinates
        max_xy (list [x,y]): Maximum x and y values
        min_xy (list, [x,y]]): minimum X,Y Defaults to [0,0].
    """
    # get the max and min x and y values from the object list
    new_min_x = min_xy[0]
    new_min_y = min_xy[1]
    max_x = max([max(obj[i][0] for i in range(2)) for obj in object_list])
    max_y = max([max(obj[i][1] for i in range(2)) for obj in object_list])
    min_x = min([min(obj[i][0] for i in range(2)) for obj in object_list])
    min_y = min([min(obj[i][1] for i in range(2)) for obj in object_list])
    # get the x and y ratios
    x_ratio = (max_xy[0] - min_xy[0]) / (max_x - min_x)
    y_ratio = (max_xy[1] - min_xy[1]) / (max_y - min_y)
    print(f"max_x: {max_x}, max_y: {max_y}")
    print(f"min_x: {min_x}, min_y: {min_y}")
    print(f"x_ratio: {x_ratio}, y_ratio: {y_ratio}")
    # create a new list of coordinates
    new_object_list = [
        (
            (
                one_range_to_another(
                    obj[0][0], min_x, max_x, new_min_x, max_xy[0]
                ),
                one_range_to_another(
                    obj[0][1], min_y, max_y, new_min_y, max_xy[1]
                ),
            ),
            (
                (obj[1][0] - min_x) * x_ratio + new_min_x,
                (obj[1][1] - min_y) * y_ratio + new_min_y,
            ),
        )
        for obj in object_list
    ]
    return new_object_list


def set_angle(divisor_list):
    """set the angle based on a list of divisors"""
    angle = 360
    while angle == 360:
        angle = (
            (360 / random.choice(divisor_list) * random.choice(divisor_list))
            % 360
        )
    return angle


def params_to_toml(params, filename="params.toml"):
    """write the parameters to a toml file"""
    with open(filename + ".toml", "w", encoding="utf-8") as file:
        toml.dump(params, file)


# # LOCAL VARIABLES
LINE_LENGTH = 150
ANGLE_DIVS = list(range(3, 15))

AXIOM = lsys.set_axiom(4)
RULES = lsys.create_rule_dict(AXIOM, 15)

PARAM_DICT = {
    "TITLE": "LSYS PARAMS",
    "N": DEFAULT["RECURSION_DEPTH"],
    "AXIOM": AXIOM,
    "RULES": RULES,
    "INITIAL_ANGLE": set_angle(ANGLE_DIVS),
    "ROTATE_ANGLE": set_angle(ANGLE_DIVS),
    "LINE_LENGTH": LINE_LENGTH,
    "START_POS": (20, 20),
    "CREATED": utils.date_string(),
}
utils.print_params(PARAM_DICT)


LINE_STYLE = {"stroke": "#fff", "stroke-width": 10, "stroke-linecap": "round"}
# LOCAL FUNCTIONS

svg_list = []

TRY_COUNT = 0
while True:
    TRY_COUNT += 1
    axiom = lsys.set_axiom(random.choice(range(1, 5)))
    rules = lsys.create_rule_dict(axiom, 15)
    divisor = random.choice(ANGLE_DIVS)
    PARAM_DICT = {
        "TITLE": "LSYS PARAMS",
        "N": divisor,
        "AXIOM": axiom,
        "RULES": rules,
        "INITIAL_ANGLE": 90,
        "ROTATE_ANGLE": 360 / divisor,
        "LINE_LENGTH": LINE_LENGTH,
        "START_POS": (20, 20),
        "CREATED": utils.date_string(),
    }
    tree = lsys.set_lsys_string(
        PARAM_DICT["AXIOM"], PARAM_DICT["RULES"], PARAM_DICT["N"]
    )

    lines = lsys.lsys_to_lines(
        tree,
        PARAM_DICT["START_POS"],
        PARAM_DICT["INITIAL_ANGLE"],
        PARAM_DICT["LINE_LENGTH"],
        PARAM_DICT["ROTATE_ANGLE"],
    )
    if len(lines) >= 5:
        break
    print(f"{tree} has {len(lines)} lines, trying again (attempt {TRY_COUNT})")
# remove duplicates from lines
lines = list(set(lines))
lines = [
    (
        (
            set_precision(line[0][0], DEFAULT["PRECISION"]),
            set_precision(line[0][1], DEFAULT["PRECISION"]),
        ),
        (
            set_precision(line[1][0], DEFAULT["PRECISION"]),
            set_precision(line[1][1], DEFAULT["PRECISION"]),
        ),
    )
    for line in lines
]


if len(lines) < 5:
    # less than 5 lines, we should break
    print("Not enough lines to draw")
    exit()
# test the lines
for line in lines:
    svg_list.append(draw.line(line[0], line[1], DEFAULT["LINE_STYLE"]))
# set precision of the lines
lines = [  # set precision of the lines
    (
        (set_precision(line[0][0]), set_precision(line[0][1])),
        (set_precision(line[1][0]), set_precision(line[1][1])),
    )
    for line in lines
]
lines = translate_coords(lines)  # translate the coordinates to have +ve values
# lines = resize_coords(
#     lines,
#     [
#         DEFAULT["IMAGE_SIZE"][0] - DEFAULT["MM_BLEED"],
#         DEFAULT["IMAGE_SIZE"][0] - DEFAULT["MM_BLEED"],
#     ],
#     (DEFAULT["MM_BLEED"], DEFAULT["MM_BLEED"]),
# )

# calculate the viewbox and paper size
set_viewbox(lines, DEFAULT["BLEED"])


DEFAULT["DRAWABLE_AREA"] = set_viewbox(lines, DEFAULT["BLEED"])
DEFAULT["PAPER_SIZE"] = set_image_size(DEFAULT["DRAWABLE_AREA"])
svg_list.append(svg.set_comment(PARAM_DICT))
utils.print_params(DEFAULT)
# fill svg_list with svg objects

doc = svg.build_svg_file(
    DEFAULT["PAPER_SIZE"],
    DEFAULT["DRAWABLE_AREA"],
    svg_list
)
DEFAULT.update(
    {
        "FILENAME": utils.create_dir(DEFAULT["OUTPUT_DIR"])
        + generate_filename(PARAM_DICT["RULES"])
        + ".svg"
    }
)
svg.write_file(DEFAULT["FILENAME"], doc)
# write the parameters to a toml file
# params_to_toml(PARAM_DICT, DEFAULT["FILENAME"])
utils.print_params(PARAM_DICT)
print(str(len(tree) * PARAM_DICT["N"]))
# print(f"Filename: {generate_filename(PARAM_DICT['RULES'])}")
