#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skeleton file for new scripts
"""

import random
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

# local libraries from the helpers directory
from modules import cli, lsys, read, svg, utils, variant


def merge_continuous_lines(lines):
    merged = True
    while merged:
        merged = False
        lines.sort(key=lambda x: (x[0], x[1]))
        
        starts_at = {}
        for i, (a, b, w) in enumerate(lines):
            starts_at.setdefault(a, []).append((b, w, i))
            
        to_remove = set()
        new_lines = []
        
        for i, (a, b, w) in enumerate(lines):
            if i in to_remove:
                continue
                
            merged_this = False
            if b in starts_at:
                for b2, w2, j in starts_at[b]:
                    if j in to_remove or i == j:
                        continue
                    if w == w2:
                        dx1 = b[0] - a[0]
                        dy1 = b[1] - a[1]
                        dx2 = b2[0] - b[0]
                        dy2 = b2[1] - b[1]
                        
                        if abs(dx1 * dy2 - dy1 * dx2) < 1e-6:
                            new_lines.append((a, b2, w))
                            to_remove.add(i)
                            to_remove.add(j)
                            merged = True
                            merged_this = True
                            break
            if not merged_this:
                new_lines.append((a, b, w))
                
        lines = new_lines

    return list(set(lines))

def optimise_travel(lines):
    if not lines:
        return []
        
    point_to_lines = {}
    for i, line in enumerate(lines):
        pt1 = line[0]
        pt2 = line[1]
        point_to_lines.setdefault(pt1, set()).add(i)
        point_to_lines.setdefault(pt2, set()).add(i)
        
    unvisited = set(range(len(lines)))
    optimized = []
    
    current_pt = lines[0][0]
    
    while unvisited:
        next_line_idx = None
        if current_pt in point_to_lines:
            for idx in point_to_lines[current_pt]:
                if idx in unvisited:
                    next_line_idx = idx
                    break
                    
        if next_line_idx is None:
            min_dist_sq = float('inf')
            best_idx = None
            
            for i in unvisited:
                l = lines[i]
                d1 = (l[0][0] - current_pt[0])**2 + (l[0][1] - current_pt[1])**2
                if d1 < min_dist_sq:
                    min_dist_sq = d1
                    best_idx = i
                
                d2 = (l[1][0] - current_pt[0])**2 + (l[1][1] - current_pt[1])**2
                if d2 < min_dist_sq:
                    min_dist_sq = d2
                    best_idx = i
                    
            next_line_idx = best_idx
            
        assert next_line_idx is not None
        l = lines[next_line_idx]
        unvisited.remove(next_line_idx)
        
        d1 = (l[0][0] - current_pt[0])**2 + (l[0][1] - current_pt[1])**2
        d2 = (l[1][0] - current_pt[0])**2 + (l[1][1] - current_pt[1])**2
        
        if d1 <= d2:
            optimized.append((l[0], l[1], l[2]))
            current_pt = l[1]
        else:
            optimized.append((l[1], l[0], l[2]))
            current_pt = l[0]
            
    return optimized


def generate_and_save_svg(PARAM_DICT, tree, lines, DEFAULT, args, base_dir):
    svg_list = []
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
    
    if DEFAULT.get("MERGE", False):
        unique_lines = merge_continuous_lines(unique_lines)

    if len(unique_lines) < 5:
        # less than 5 lines, we should break
        sys.exit("Not enough lines to draw")

    # scale and center the lines to fit exactly within IMAGE_SIZE
    scaled_lines = svg.scale_to_fit(
        unique_lines, DEFAULT["IMAGE_SIZE"], DEFAULT["BLEED"]
    )

    # group and draw the lines
    groups = {}
    for line in scaled_lines:
        style = DEFAULT.get("LINE_STYLE", {}).copy()
        if line[2] is not None:
            style["stroke-width"] = line[2]
        
        style_key = tuple(sorted(style.items()))
        if style_key not in groups:
            groups[style_key] = []
        groups[style_key].append(line)

    for style_key, lines in groups.items():
        if DEFAULT.get("OPTIMISE_TRAVEL", False):
            lines = optimise_travel(lines)
            
        style_dict = dict(style_key)
        group_style = svg.dict_to_tags(style_dict)
        group_tag = f"<g {group_style}>" if group_style else "<g>"
        svg_list.append(group_tag)
        for line in lines:
            svg_list.append(svg.line(line[0], line[1]))
        svg_list.append("</g>")

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
    
    filename_pref = DEFAULT.get("FILENAME")
    if filename_pref == "datetime":
        base_filename = utils.date_string()
    elif filename_pref == "unix":
        base_filename = str(int(time.time() * 1000))
    else:
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
            "OUTPUT_FILEPATH": str(
                Path(utils.create_dir(output_dir)).resolve()
                / f"{base_filename}.svg"
            )
        }
    )
    svg.write_file(DEFAULT["OUTPUT_FILEPATH"], doc)
    utils.print_params(PARAM_DICT)
    print(str(len(tree) * PARAM_DICT["N"]))


def main():
    args = cli.get_args()

    if args.read:
        command = read.build_commandline(args.read)
        if command:
            print(command)
        else:
            print(f"Could not read params from {args.read}")
        return

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
    if args.filename is not None:
        DEFAULT["FILENAME"] = args.filename
    if getattr(args, 'merge', None) is not None:
        DEFAULT["MERGE"] = args.merge
    if getattr(args, 'optimise_travel', None) is not None:
        DEFAULT["OPTIMISE_TRAVEL"] = args.optimise_travel

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
    elif args.variant:
        command = read.extract_comment(args.variant)
        if not command:
            sys.exit(f"Could not read params from {args.variant}")
        base_params = read.parse_comment(command)
        
        if "RULES" in base_params:
            parsed_string = utils.string_to_dict(base_params["RULES"].replace('{', '').replace('}', ''))
            base_params["RULES"] = parsed_string
            
        PARAM_DICT = variant.generate_variant(base_params, DEFAULT.get("VARIANT_CONSTRAINTS", {}))
        
        PARAM_DICT["TITLE"] = "VARIANT LSYS"
        PARAM_DICT["N"] = int(PARAM_DICT["N"])
        PARAM_DICT["INITIAL_ANGLE"] = float(PARAM_DICT["INITIAL_ANGLE"])
        PARAM_DICT["ROTATE_ANGLE"] = float(PARAM_DICT["ROTATE_ANGLE"])
        PARAM_DICT["LINE_LENGTH"] = float(PARAM_DICT["LINE_LENGTH"])
        PARAM_DICT["CREATED"] = utils.date_string()
        
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
    elif args.iterate:
        command = read.extract_comment(args.iterate)
        if not command:
            sys.exit(f"Could not read params from {args.iterate}")
        base_params = read.parse_comment(command)
        
        if "RULES" in base_params:
            parsed_string = utils.string_to_dict(base_params["RULES"].replace('{', '').replace('}', ''))
            base_params["RULES"] = parsed_string
            
        constraints = DEFAULT.get("VARIANT_CONSTRAINTS", {})
        iterate_only = constraints.get("ITERATED_PARAMETERS", ["rules", "N", "angles"])
        
        for i in range(args.iterations):
            base_params = variant.generate_variant(base_params, constraints, iterate_only)
            PARAM_DICT = base_params.copy()
            PARAM_DICT["TITLE"] = f"ITERATION {i+1}"
            PARAM_DICT["N"] = int(PARAM_DICT["N"])
            PARAM_DICT["INITIAL_ANGLE"] = float(PARAM_DICT["INITIAL_ANGLE"])
            PARAM_DICT["ROTATE_ANGLE"] = float(PARAM_DICT["ROTATE_ANGLE"])
            PARAM_DICT["LINE_LENGTH"] = float(PARAM_DICT["LINE_LENGTH"])
            PARAM_DICT["CREATED"] = utils.date_string()
            
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
            
            generate_and_save_svg(PARAM_DICT, tree, lines, DEFAULT, args, base_dir)
            
        return
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

    generate_and_save_svg(PARAM_DICT, tree, lines, DEFAULT, args, base_dir)


if __name__ == "__main__":
    main()
