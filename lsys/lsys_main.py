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
    LINE_LENGTH = DEFAULT.get("LINE_LENGTH", 150)
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
        "INITIAL_ANGLE": args.initial_angle if args.initial_angle is not None else lsys.set_angle(ANGLE_DIVS),
        "ROTATE_ANGLE": args.rotation if args.rotation is not None else lsys.set_angle(ANGLE_DIVS),
        "LINE_LENGTH": LINE_LENGTH,
        "CREATED": utils.date_string(),
    }
    utils.print_params(PARAM_DICT)

    svg_list = []

    TRY_COUNT = 0
    if args.rules:
        parsed_string = utils.string_to_dict(args.rules)
        if "str" in parsed_string and len(parsed_string) == 1:
            tree = parsed_string["str"]
            axiom = "N/A"
            rules = {}
            n_iters = 1
        else:
            rules = parsed_string
            axiom = args.axiom
            n_iters = RECURSION_DEPTH
            tree = lsys.set_lsys_string(axiom, rules, n_iters)

        divisor = random.choice(ANGLE_DIVS)
        PARAM_DICT = {
            "TITLE": args.title if args.title is not None else "USER DEFINED LSYS",
            "PARADIGM": "N/A",
            "N": n_iters,
            "AXIOM": axiom,
            "RULES": rules,
            "INITIAL_ANGLE": args.initial_angle if args.initial_angle is not None else 90,
            "ROTATE_ANGLE": args.rotation if args.rotation is not None else 360 / divisor,
            "LINE_LENGTH": LINE_LENGTH,
            "CREATED": utils.date_string(),
        }
        lines = lsys.lsys_to_lines(
            tree,
            PARAM_DICT["INITIAL_ANGLE"],
            PARAM_DICT["LINE_LENGTH"],
            PARAM_DICT["ROTATE_ANGLE"],
            weight=DEFAULT.get("LINE_STYLE", {}).get("stroke-width", 10),
            scale=args.scale,
            angle_increment=args.angle_increment,
            weight_increment=args.weight_increment
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
                "INITIAL_ANGLE": args.initial_angle if args.initial_angle is not None else 90,
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
                weight=DEFAULT.get("LINE_STYLE", {}).get("stroke-width", 10),
                scale=args.scale,
                angle_increment=args.angle_increment,
                weight_increment=args.weight_increment
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
        processed_lines.append((pts[0], pts[1], line[2]))
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
        style = DEFAULT["LINE_STYLE"].copy()
        if line[2] is not None:
            style["stroke-width"] = line[2]
        svg_list.append(svg.line(line[0], line[1], style))

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
    
    if args.rules:
        parsed_string = utils.string_to_dict(args.rules)
        if "str" in parsed_string and len(parsed_string) == 1:
            base_filename = lsys.generate_filename(parsed_string)
        else:
            base_filename = lsys.generate_filename(parsed_string)
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
