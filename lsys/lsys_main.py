#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skeleton file for new scripts
"""

import random
import sys
import tomllib
from pathlib import Path
from typing import Any

# local libraries from the helpers directory
from modules import cli, lsys, svg, utils


def main():
    args = cli.get_args()

    # Load config file and set DEFAULT parameters
    base_dir = Path(__file__).resolve().parent
    with (base_dir / "config.toml").open("rb") as file:
        config = tomllib.load(file)
    DEFAULT: dict[str, Any] = config["DEFAULT"]

    if args.title is not None:
        DEFAULT["TITLE"] = args.title
    if args.paradigm is not None:
        DEFAULT["PARADIGM"] = args.paradigm
    if args.bleed is not None:
        DEFAULT["BLEED"] = args.bleed
    if args.options_per_rule is not None:
        DEFAULT["OPTIONS_PER_RULE"] = args.options_per_rule
    if args.ppmm is not None:
        DEFAULT["PPMM"] = args.ppmm
    if args.paper_size is not None:
        DEFAULT["PAPER_SIZE"] = args.paper_size
    if args.background_color is not None:
        DEFAULT["BACKGROUND_COLOR"] = args.background_color
    if args.precision is not None:
        DEFAULT["PRECISION"] = args.precision
    if args.angle_divisors is not None:
        DEFAULT["ANGLE_DIVISORS"] = args.angle_divisors
    if args.output_dir is not None:
        DEFAULT["OUTPUT_DIR"] = args.output_dir

    DEFAULT.update(
        {
            "IMAGE_SIZE": [
                DEFAULT["PAPER_SIZE"][0] * DEFAULT["PPMM"],
                DEFAULT["PAPER_SIZE"][1] * DEFAULT["PPMM"],
            ]
        }
    )
    DEFAULT.update({"BLEED": DEFAULT["BLEED"] * DEFAULT["PPMM"]})

    print(f"Default parameters: {DEFAULT}")

    # LOCAL VARIABLES
    LINE_LENGTH = 150
    ANGLE_DIVS = DEFAULT.get("ANGLE_DIVISORS", [3, 4, 5, 6, 8, 10, 12])
    RECURSION_DEPTH = args.recursion if args.recursion is not None else DEFAULT["RECURSION_DEPTH"]

    AXIOM = lsys.set_axiom(4)
    PARADIGM = DEFAULT.get("PARADIGM", "geometric")
    RULES = lsys.create_rule_dict(AXIOM, 15, paradigm=PARADIGM)

    PARAM_DICT = {
        "TITLE": "LSYS PARAMS",
        "PARADIGM": PARADIGM,
        "N": DEFAULT["RECURSION_DEPTH"],
        "AXIOM": AXIOM,
        "RULES": RULES,
        "INITIAL_ANGLE": args.angle if args.angle is not None else lsys.set_angle(ANGLE_DIVS),
        "ROTATE_ANGLE": args.rotation if args.rotation is not None else lsys.set_angle(ANGLE_DIVS),
        "LINE_LENGTH": LINE_LENGTH,
        "CREATED": utils.date_string(),
    }
    utils.print_params(PARAM_DICT)

    svg_list = []

    TRY_COUNT = 0
    if args.string:
        tree = args.string
        divisor = random.choice(ANGLE_DIVS)
        PARAM_DICT = {
            "TITLE": "USER DEFINED LSYS",
            "PARADIGM": "N/A",
            "N": 1,
            "AXIOM": "N/A",
            "RULES": {},
            "INITIAL_ANGLE": args.angle if args.angle is not None else 90,
            "ROTATE_ANGLE": args.rotation if args.rotation is not None else 360 / divisor,
            "LINE_LENGTH": LINE_LENGTH,
            "CREATED": utils.date_string(),
        }
        lines = lsys.lsys_to_lines(
            tree,
            PARAM_DICT["INITIAL_ANGLE"],
            PARAM_DICT["LINE_LENGTH"],
            PARAM_DICT["ROTATE_ANGLE"],
        )
    else:
        while True:
            TRY_COUNT += 1
            axiom = lsys.set_axiom(random.choice(range(1, 5)))
            PARADIGM = DEFAULT.get("PARADIGM", "geometric")
            OPTIONS = DEFAULT.get("OPTIONS_PER_RULE", 3)
            rules = lsys.create_rule_dict(
                axiom, 15, paradigm=PARADIGM, options_per_rule=OPTIONS
            )
            divisor = random.choice(ANGLE_DIVS)
            PARAM_DICT = {
                "TITLE": "LSYS PARAMS",
                "PARADIGM": PARADIGM,
                "N": RECURSION_DEPTH,
                "AXIOM": axiom,
                "RULES": rules,
                "INITIAL_ANGLE": args.angle if args.angle is not None else 90,
                "ROTATE_ANGLE": args.rotation if args.rotation is not None else 360 / divisor,
                "LINE_LENGTH": LINE_LENGTH,
                "CREATED": utils.date_string(),
            }
            tree = lsys.set_lsys_string(
                PARAM_DICT["AXIOM"], PARAM_DICT["RULES"], PARAM_DICT["N"]
            )

            lines = lsys.lsys_to_lines(
                tree,
                PARAM_DICT["INITIAL_ANGLE"],
                PARAM_DICT["LINE_LENGTH"],
                PARAM_DICT["ROTATE_ANGLE"],
            )
            if len(lines) >= 5:
                break
            print(f"{tree} has {len(lines)} lines, trying again (attempt {TRY_COUNT})")

    # apply precision, sort points to handle backwards lines, and remove duplicates
    processed_lines = []
    for line in lines:
        pts = sorted(
            [
                (
                    utils.set_precision(line[0][0], DEFAULT["PRECISION"]),
                    utils.set_precision(line[0][1], DEFAULT["PRECISION"]),
                ),
                (
                    utils.set_precision(line[1][0], DEFAULT["PRECISION"]),
                    utils.set_precision(line[1][1], DEFAULT["PRECISION"]),
                ),
            ]
        )
        processed_lines.append((pts[0], pts[1]))
    unique_lines = list(set(processed_lines))

    if len(unique_lines) < 5:
        # less than 5 lines, we should break
        sys.exit("Not enough lines to draw")

    # scale and center the lines to fit exactly within IMAGE_SIZE
    scaled_lines = svg.scale_to_fit(
        unique_lines, DEFAULT["IMAGE_SIZE"], DEFAULT["BLEED"]
    )

    # draw the lines
    for line in scaled_lines:
        svg_list.append(svg.line(line[0], line[1], DEFAULT["LINE_STYLE"]))

    # set the viewbox and paper size to the requested IMAGE_SIZE
    DEFAULT["PAPER_SIZE"] = DEFAULT["IMAGE_SIZE"]
    DEFAULT["DRAWABLE_AREA"] = (
        0,
        0,
        DEFAULT["IMAGE_SIZE"][0],
        DEFAULT["IMAGE_SIZE"][1],
    )

    svg_list.append(svg.set_comment(PARAM_DICT))
    utils.print_params(DEFAULT)

    # fill svg_list with svg objects
    doc = svg.build_svg_file(
        DEFAULT["PAPER_SIZE"],
        DEFAULT["DRAWABLE_AREA"],
        svg_list,
        background=DEFAULT.get("BACKGROUND_COLOR", "white"),
    )
    output_dir = base_dir / DEFAULT["OUTPUT_DIR"]
    
    if args.string:
        base_filename = lsys.generate_filename(utils.string_to_dict(args.string[:200]))
    else:
        base_filename = lsys.generate_filename(PARAM_DICT['RULES'])
        
    DEFAULT.update(
        {
            "FILENAME": str(
                Path(utils.create_dir(output_dir)).resolve()
                / f"{base_filename}.svg"
            )
        }
    )
    svg.write_file(DEFAULT["FILENAME"], doc)
    utils.print_params(PARAM_DICT)
    print(str(len(tree) * PARAM_DICT["N"]))


if __name__ == "__main__":
    main()
