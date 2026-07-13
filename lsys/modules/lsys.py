"""L-System Functions"""

import random
from math import cos, sin, radians
import re
from typing import Any


def set_lsys_string(axiom: str, rules: dict[str, str | list[str]], n: int, max_length: int = 100000) -> str:
    """
    Generates a string of characters based on the axiom and rules.
    """
    string = axiom
    for _ in range(n):
        # Safety check to prevent exponential memory overflow
        if len(string) > (max_length // 10):
            print(f"Stopping early to prevent memory overflow (Length: {len(string)})")
            break

        next_string = ""
        for c in string:
            replacement = rules.get(c, c)
            if isinstance(replacement, list):
                next_string += random.choice(replacement)
            else:
                next_string += replacement
        string = next_string

        if len(string) >= max_length:
            print("Reached max_length during generation.")
            break

    if not is_valid_rule(string):
        print(f"Invalid rule: {string}")
    return string


def lsys_to_lines(
    lsys: str, 
    angle: float, 
    length: float, 
    angle_offset: float,
    weight: float = 1.0,
    scale: float = 1.2,
    angle_increment: float = 15.0,
    weight_increment: float = 1.0
) -> set[tuple[tuple[float, float], tuple[float, float], float]]:
    """
    Generates a list of lines from a string of characters.

    Parameters:
    lsys (str):             The string of characters to convert to lines.
    angle (float):          The initial heading angle.
    length (float):         The starting length of the lines.
    angle_offset (float):   The step angle.
    weight (float):         The initial line width.
    scale (float):          Multiplier for length changes.
    angle_increment (float):Amount to adjust step angle.
    weight_increment (float):Amount to adjust line width.

    Returns:
    set: A set of lines generated from the string of characters.
    """
    lines = []
    stack = []
    x, y = 0.0, 0.0
    rotation_direction = 1

    i = 0
    while i < len(lsys):
        c = lsys[i]
        if c in ("F", "G"):
            count = 1
            while i + count < len(lsys) and lsys[i + count] == c:
                count += 1
            x2 = x - length * count * cos(radians(angle))
            y2 = y - length * count * sin(radians(angle))
            lines.append(((x, y), (x2, y2), weight))
            x, y = x2, y2
            i += count - 1
        elif c == "f":
            x2 = x - length * cos(radians(angle))
            y2 = y - length * sin(radians(angle))
            x, y = x2, y2
        elif c == "+":
            angle += angle_offset * rotation_direction
        elif c == "-":
            angle += angle_offset * -rotation_direction
        elif c == "|":
            angle += 180
        elif c == "[":
            stack.append((x, y, angle, angle_offset, length, weight, rotation_direction))
        elif c == "]":
            if stack:
                x, y, angle, angle_offset, length, weight, rotation_direction = stack.pop()
        elif c == "#":
            weight += weight_increment
        elif c == "!":
            weight -= weight_increment
        elif c == ">":
            length *= scale
        elif c == "<":
            length /= scale
        elif c == "&":
            rotation_direction = -rotation_direction
        elif c == "(":
            angle_offset += angle_increment
        elif c == ")":
            angle_offset -= angle_increment
        i += 1

    return set(lines)


def cleanse_rule(rule_string: str) -> str:
    """replaces cancelling characters in a rule string
    ensures that the rule string will produce a logical
    result when applied to the axiom

    Args:
        rule_string (string): a string of characters

    Returns:
        rule_string (string): a string of characters without cancelling
        sequences of characters
    """

    # Only remove sequences that preserve branch structure.
    previous = ""
    while rule_string != previous:
        previous = rule_string
        rule_string = re.sub(r"\[\]|\+-|-\+|!#|#!|\(\)|\)\(|<>|><|!!", "", rule_string)
    return rule_string


def is_valid_rule(rule_string: str) -> bool:
    """checks if a rule string is valid"""
    # if no F directive, return False
    if "F" not in rule_string:
        return False
    if rule_string == "F" * len(rule_string):
        return False
    # if no + or - directive, return False
    if "+" not in rule_string and "-" not in rule_string:
        return False
    return True


def create_stochastic_rule_dict(axiom: str, length: int, options_per_rule: int = 3) -> dict[str, list[str]]:
    """creates a randomized/organic dictionary of rules"""
    rules = {}
    for char in axiom:
        options = []
        for _ in range(options_per_rule):
            rules_str = "F"
            stack = []
            for _ in range(length):
                choices = ["F", "+", "-", "[", "]"]

                # Prevent opposite or redundant sequences
                if rules_str:
                    last_char = rules_str[-1]
                    if last_char == "+":
                        choices.remove("-")
                    elif last_char == "-":
                        choices.remove("+")
                    elif last_char == "[":
                        choices.remove("]")
                        choices.remove("[")
                    elif last_char == "]":
                        choices.remove("[")
                        choices.remove("]")

                character = random.choice(choices)

                if character == "[":
                    stack.append(character)
                if character == "]":
                    if stack:
                        stack.pop()
                    else:
                        continue  # Skip unmatched pop
                rules_str += character
            # close unmatched brackets
            while stack:
                rules_str += "]"
                stack.pop()
            options.append(cleanse_rule(rules_str))
        rules[char] = options
    return rules


def create_geometric_rule_dict(axiom: str, length: int) -> dict[str, str]:
    """creates a symmetrical/balanced dictionary of rules"""
    rules = {}
    for char in axiom:
        rules_str = "F"
        stack = []
        angle_balance = 0
        for _ in range(length):
            # Prefer balanced turns
            if angle_balance > 0:
                character = random.choice(["F", "-", "[", "]"])
            elif angle_balance < 0:
                character = random.choice(["F", "+", "[", "]"])
            else:
                character = random.choice(["F", "+", "-", "[", "]"])

            if character == "+":
                angle_balance += 1
            if character == "-":
                angle_balance -= 1

            if character == "[":
                stack.append(angle_balance)
            if character == "]":
                if stack:
                    angle_balance = stack.pop()
                else:
                    continue
            rules_str += character

        while stack:
            rules_str += "]"
            stack.pop()
        rules[char] = cleanse_rule(rules_str)
    return rules


def create_extended_stochastic_rule_dict(axiom: str, length: int, options_per_rule: int = 3) -> dict[str, list[str]]:
    """creates a randomized/organic dictionary of rules using the extended instruction set"""
    rules = {}
    for char in axiom:
        options = []
        for _ in range(options_per_rule):
            rules_str = "F"
            stack = []
            for _ in range(length):
                choices = ["F", "+", "-", "[", "]", "f", "|", "#", "!", ">", "<", "&", "(", ")"]

                # Prevent opposite or redundant sequences
                if rules_str:
                    last_char = rules_str[-1]
                    if last_char == "+":
                        choices.remove("-")
                    elif last_char == "-":
                        choices.remove("+")
                    elif last_char == "[":
                        choices.remove("]")
                        choices.remove("[")
                    elif last_char == "]":
                        choices.remove("[")
                        choices.remove("]")
                    elif last_char == "!":
                        if "#" in choices: choices.remove("#")
                        if "!" in choices: choices.remove("!")
                    elif last_char == "#":
                        if "!" in choices: choices.remove("!")
                    elif last_char == "(":
                        if ")" in choices: choices.remove(")")
                    elif last_char == ")":
                        if "(" in choices: choices.remove("(")
                    elif last_char == "<":
                        if ">" in choices: choices.remove(">")
                    elif last_char == ">":
                        if "<" in choices: choices.remove("<")

                character = random.choice(choices)

                if character == "[":
                    stack.append(character)
                if character == "]":
                    if stack:
                        stack.pop()
                    else:
                        continue  # Skip unmatched pop
                rules_str += character
            # close unmatched brackets
            while stack:
                rules_str += "]"
                stack.pop()
            options.append(cleanse_rule(rules_str))
        rules[char] = options
    return rules


def create_extended_geometric_rule_dict(axiom: str, length: int) -> dict[str, str]:
    """creates a symmetrical/balanced dictionary of rules using the extended instruction set"""
    rules = {}
    for char in axiom:
        rules_str = "F"
        stack = []
        angle_balance = 0
        for _ in range(length):
            # Prefer balanced turns
            if angle_balance > 0:
                choices = ["F", "-", "[", "]", "f", "|", "#", "!", ">", "<", "&", "(", ")"]
            elif angle_balance < 0:
                choices = ["F", "+", "[", "]", "f", "|", "#", "!", ">", "<", "&", "(", ")"]
            else:
                choices = ["F", "+", "-", "[", "]", "f", "|", "#", "!", ">", "<", "&", "(", ")"]

            if rules_str:
                last_char = rules_str[-1]
                if last_char == "+":
                    if "-" in choices: choices.remove("-")
                elif last_char == "-":
                    if "+" in choices: choices.remove("+")
                elif last_char == "[":
                    if "]" in choices: choices.remove("]")
                    if "[" in choices: choices.remove("[")
                elif last_char == "]":
                    if "[" in choices: choices.remove("[")
                    if "]" in choices: choices.remove("]")
                elif last_char == "!":
                    if "#" in choices: choices.remove("#")
                    if "!" in choices: choices.remove("!")
                elif last_char == "#":
                    if "!" in choices: choices.remove("!")
                elif last_char == "(":
                    if ")" in choices: choices.remove(")")
                elif last_char == ")":
                    if "(" in choices: choices.remove("(")
                elif last_char == "<":
                    if ">" in choices: choices.remove(">")
                elif last_char == ">":
                    if "<" in choices: choices.remove("<")

            character = random.choice(choices)

            if character == "+":
                angle_balance += 1
            if character == "-":
                angle_balance -= 1

            if character == "[":
                stack.append(angle_balance)
            if character == "]":
                if stack:
                    angle_balance = stack.pop()
                else:
                    continue
            rules_str += character

        while stack:
            rules_str += "]"
            stack.pop()
        rules[char] = cleanse_rule(rules_str)
    return rules


def create_rule_dict(axiom: str, length: int, paradigm: str = "geometric", options_per_rule: int = 3) -> dict[str, Any]:
    """Router for creating rule dictionaries based on paradigm"""
    if paradigm == "stochastic":
        return create_stochastic_rule_dict(axiom, length, options_per_rule)
    elif paradigm == "extended-stochastic":
        return create_extended_stochastic_rule_dict(axiom, length, options_per_rule)
    elif paradigm == "extended-geometric":
        return create_extended_geometric_rule_dict(axiom, length)
    else:
        return create_geometric_rule_dict(axiom, length)


def set_axiom(length: int) -> str:
    """returns a random axiom string"""
    axiom = "F"
    length = random.randint(1, length)
    letters = "xyzabcde"
    if length > 1:
        axiom += letters[:length]
    return axiom


def generate_filename(rules_dict: dict[str, Any]) -> str:
    """return a string which can be used as a filename"""
    # rules is a dictionary, expand it to a string
    # print the length of the dictionary
    print(f"Length of rules_dict: {len(rules_dict)}")
    rule_string = ""
    for key, value in rules_dict.items():
        val_str = "".join(value) if isinstance(value, list) else str(value)
        print(f"{key}-->{val_str}")
        rule_string += f"{key}→{val_str},"
        # strip final comma, and return
    rule_string = rule_string.rstrip(",")
    return rule_string


def set_angle(divisor_list: list[int]) -> float:
    """set the angle based on a list of divisors"""
    angle = 360
    while angle == 360:
        angle = (360 / random.choice(divisor_list) * random.choice(divisor_list)) % 360
    return angle
