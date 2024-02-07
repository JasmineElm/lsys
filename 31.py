#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Skeleton file for new scripts
"""
import random
import toml

# local libraries
from helpers import svg, utils, lsys, draw

# Load config file and set DEFAULT parameters
config = toml.load("config.toml")
DEFAULT = config["DEFAULT"]
DEFAULT.update({"FILENAME": utils.create_dir(
    DEFAULT['OUTPUT_DIR']) + utils.generate_filename()})


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
    viewbox = (min_x//1, min_y//1, (1 + max_x - min_x) //
               1, (1 + max_y - min_y)//1)
    return viewbox


def set_image_size(viewbox):
    """set the image size based on the viewbox"""
    return ((viewbox[2]-viewbox[0]),
            (viewbox[3]-viewbox[1]))


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
    new_object_list = [((obj[0][0] + x_offset, obj[0][1] + y_offset),
                        (obj[1][0] + x_offset, obj[1][1] + y_offset)) for obj in object_list]
    return new_object_list




def set_angle(divisor_list):
    """set the angle based on a list of divisors"""
    angle = 360
    while angle == 360:
        angle = (360/random.choice(divisor_list) *
                 random.choice(divisor_list)) % 360
    return angle

# # LOCAL VARIABLES
LINE_LENGTH = 150
ANGLE_DIVS = list(range(3, 9))

AXIOM = lsys.set_axiom(4)
RULES = lsys.create_rule_dict(AXIOM, 15)

PARAM_DICT = {"TITLE": "LSYS PARAMS", "N": 5, "AXIOM": AXIOM,
              "RULES": RULES,
              "INITIAL_ANGLE": 360/random.choice(ANGLE_DIVS),
              "ROTATE_ANGLE": 360/random.choice(ANGLE_DIVS),
              "LINE_LENGTH": LINE_LENGTH,
              "START_POS": (0, 0),
              "CREATED": utils.date_string()}
utils.print_params(PARAM_DICT)


LINE_STYLE = {'stroke': '#fff', 'stroke-width': 10, "stroke-linecap": "round"}
# LOCAL FUNCTIONS

svg_list = []

try_count = 0
while True:
    try_count += 1
    axiom = lsys.set_axiom(4)
    rules = lsys.create_rule_dict(axiom, 15)
    PARAM_DICT = {"TITLE": "LSYS PARAMS",
                  "N": 5,
                  "AXIOM": axiom,
                  "RULES": rules,
                  "INITIAL_ANGLE": 90,
                  #   "INITIAL_ANGLE": 360/random.choice(ANGLE_DIVS)*random.choice(ANGLE_DIVS),
                  "ROTATE_ANGLE": set_angle(ANGLE_DIVS),
                  "LINE_LENGTH": LINE_LENGTH,
                  "START_POS": (0, 0),
                  "CREATED": utils.date_string()}
    tree = lsys.set_lsys_string(PARAM_DICT["AXIOM"],
                                PARAM_DICT["RULES"],
                                PARAM_DICT["N"])

    lines = lsys.lsys_to_lines(tree, PARAM_DICT["START_POS"],
                               PARAM_DICT["INITIAL_ANGLE"],
                               PARAM_DICT["LINE_LENGTH"],
                               PARAM_DICT["ROTATE_ANGLE"])
    if len(lines) >= 5:
        break
    print(f"{tree} has {len(lines)} lines, trying again (attempt {try_count})")

lines = [((set_precision(line[0][0]), set_precision(line[0][1])),
          (set_precision(line[1][0]), set_precision(line[1][1]))) for line in lines]
lines = translate_coords(lines)
DEFAULT['DRAWABLE_AREA'] = set_viewbox(lines, DEFAULT['BLEED'])
DEFAULT['PAPER_SIZE'] = set_image_size(DEFAULT['DRAWABLE_AREA']
                                       )
svg_list.append(svg.set_comment(PARAM_DICT))
utils.print_params(DEFAULT)
if len(lines) < 5:
    # less than 5 lines, we should break
    print("Not enough lines to draw")
    exit()
for line in lines:
    svg_list.append(draw.line(line[0], line[1], DEFAULT['LINE_STYLE']))
# fill svg_list with svg objects

doc = svg.build_svg_file(DEFAULT['PAPER_SIZE'],
                         DEFAULT['DRAWABLE_AREA'],
                         svg_list)


svg.write_file(DEFAULT['FILENAME'], doc)
utils.print_params(PARAM_DICT)
print(str(len(tree)*PARAM_DICT["N"]))

