"""L-System Functions
"""
import random
import math


def set_lsys_string(axiom, rules, n):
    """
    Generates a string of characters based on the axiom and rules.

    Parameters:
    axiom (str): The starting string.
    rules (dict): A dictionary of rules to apply to the string.
    n (int): The number of iterations to perform.

    Returns:
    str: A string of characters generated by applying the rules to the axiom.
    """
    string = axiom
    for _ in range(n):
        string = "".join([rules.get(c, c) for c in string])
    return string


def lsys_to_lines(lsys, start_xy, angle, length, angle_offset):
    """
    Generates a list of lines from a string of characters.

    Parameters:
    lsys (str): The string of characters to convert to lines.
    start_xy (tuple): The starting coordinates of the lines.
    angle (float): The angle of the lines.
    length (float): The length of the lines.
    angle_offset (float): The angle offset to apply to the lines.

    Returns:
    list: A list of lines generated from the string of characters.
    """
    lines = []
    stack = []
    x, y = start_xy
    for c in lsys:
        if c == "F":
            x2 = x - length * math.cos(math.radians(angle))
            y2 = y - length * math.sin(math.radians(angle))
            lines.append(((x, y), (x2, y2)))
            x, y = x2, y2
        elif c == "+":
            angle += angle_offset
        elif c == "-":
            angle -= angle_offset
        elif c == "[":
            stack.append((x, y, angle))
        elif c == "]":
            x, y, angle = stack.pop()
        elif c == "X":
            pass
    return lines


def validate_rule_string(rule_string):
    rule_string = rule_string.replace(
        "[]", "").replace("+-", "").replace("-+", "")
    # remove unmatched brackets
    return rule_string


def create_rule_dict(axiom, length):
    directives = ["F", "+", "-", "[", "]"]
    # extend directives to include axiom if not already present
    for char in axiom:
        if char not in directives:
            directives.append(char)
    rules = {}
    for char in axiom:
        rules[char] = ""
        stack = []
        for _ in range(length):
            character = random.choice(directives)
            if character == "[":
                stack.append(character)
            if character == "]":
                if stack:
                    stack.pop()
                else:
                    character = ""
            rules[char] += character
        # remove unmatched brackets
        while stack:
            rules[char] = rules[char].rpartition('[')[0]
            stack.pop()
        rules[char] = validate_rule_string(rules[char])
    return rules


def explain_rules(rules):
    directives = {"F": "draw", "+": "turn left",
                  "-": "turn right", "[": "save position",
                  "]": "restore position"}
    if len(rules) > 1:
        for key in rules:
            for char in rules[key]:
                if char not in directives:
                    rules[key] = rules[key].replace(char, rules[char])
    explanation = ""
    for key in rules:
        # build the directives string
        explanation += f"{key} -> {rules[key]} \n" + \
            "\n".join([directives[char] for char in rules[key]]) + "\n"
        return explanation


def expand_rules(rules):
    directives = ["F", "+", "-", "[", "]"]
    for key in rules:
        for char in rules[key]:
            if char not in directives:
                rules[key] = rules[key].replace(char, rules[char])
    return rules


def set_axiom(length):
    axiom = "F"
    length = random.randint(1, length)
    letters = "xyzabcde"
    length = random.randint(1, length)
    if length > 1:
        axiom += letters[:length]
    return axiom
