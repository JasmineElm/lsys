import random
from typing import Any
from . import lsys

def mutate_rule_string(rule_string: str, rate: float, allowed: list[str]) -> str:
    """Mutates a rule string by replacing, inserting, or deleting characters based on rate."""
    new_rule = ""
    for char in rule_string:
        if random.random() < rate:
            mutation_type = random.choice(["replace", "insert", "delete"])
            if mutation_type == "replace":
                new_rule += random.choice(allowed)
            elif mutation_type == "insert":
                new_rule += char + random.choice(allowed)
            elif mutation_type == "delete":
                pass  # Skip adding the char
        else:
            new_rule += char
    
    # Cleanse and ensure validity
    new_rule = lsys.cleanse_rule(new_rule)
    if not lsys.is_valid_rule(new_rule):
        return rule_string # fallback to original if invalid
    return new_rule

def mutate_rules(rules: dict[str, str | list[str]], rate: float, allowed: list[str]) -> dict[str, str | list[str]]:
    """Mutates all rules in a rules dictionary."""
    new_rules = {}
    for key, value in rules.items():
        if isinstance(value, str):
            new_rules[key] = mutate_rule_string(value, rate, allowed)
        elif isinstance(value, list):
            new_rules[key] = [mutate_rule_string(v, rate, allowed) for v in value]
    return new_rules

def mutate_n(n: int, max_change: int) -> int:
    """Mutates recursion depth N."""
    change = random.randint(-max_change, max_change)
    return max(1, n + change)

def mutate_angle(angle: float, max_change: float) -> float:
    """Mutates an angle by up to max_change degrees."""
    change = random.uniform(-max_change, max_change)
    return (angle + change) % 360

def generate_variant(base_params: dict[str, Any], constraints: dict[str, Any], iterate_only: list[str] | None = None) -> dict[str, Any]:
    """Generates a variant PARAM_DICT based on base_params and constraints."""
    rate = constraints.get("RULE_MUTATION_RATE", 0.1)
    allowed = constraints.get("ALLOWED_MUTATIONS", ["F", "+", "-", "[", "]"])
    max_n = constraints.get("MAX_N_CHANGE", 1)
    max_angle = constraints.get("MAX_ANGLE_CHANGE", 15.0)

    variant_params = base_params.copy()
    
    # Mutate Rules
    if "RULES" in variant_params and isinstance(variant_params["RULES"], dict) and (iterate_only is None or "rules" in iterate_only):
        variant_params["RULES"] = mutate_rules(variant_params["RULES"], rate, allowed)
        
    # Mutate N
    if "N" in variant_params and (iterate_only is None or "N" in iterate_only):
        variant_params["N"] = mutate_n(int(variant_params["N"]), max_n)
        
    # Mutate Angles
    if iterate_only is None or "angles" in iterate_only:
        if "INITIAL_ANGLE" in variant_params:
            variant_params["INITIAL_ANGLE"] = mutate_angle(float(variant_params["INITIAL_ANGLE"]), max_angle)
        if "ROTATE_ANGLE" in variant_params:
            variant_params["ROTATE_ANGLE"] = mutate_angle(float(variant_params["ROTATE_ANGLE"]), max_angle)
        
    return variant_params
