import re

def extract_comment(filepath: str) -> str:
    """Read an SVG and extract the LSYS PARAMS comment."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Looking for a comment block containing TITLE
    match = re.search(r'<!--\s*(TITLE:.*?)\s*-->', content, re.DOTALL)
    if match:
        return match.group(1)
    return ""

def parse_comment(comment_text: str) -> dict:
    """Parse the comment text into a dictionary."""
    params = {}
    for line in comment_text.strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            params[key.strip()] = val.strip()
    return params

def build_commandline(filepath: str) -> str:
    """Extract comment from SVG and build the command line arguments to recreate it."""
    comment = extract_comment(filepath)
    if not comment:
        return ""
    
    params = parse_comment(comment)
    
    # Map comment keys to CLI flags
    # N -> --recursion
    # AXIOM -> --axiom
    # RULES -> --rules
    # INITIAL_ANGLE -> --initial-angle
    # ROTATE_ANGLE -> --rotation
    # PARADIGM -> --paradigm
    
    cli_args = []
    
    if "RULES" in params:
        rules_str = params['RULES'].replace('{', '').replace('}', '')
        cli_args.append(f"--rules \"{rules_str}\"")
    if "AXIOM" in params:
        cli_args.append(f"--axiom {params['AXIOM']}")
    if "N" in params:
        cli_args.append(f"--recursion {params['N']}")
    if "INITIAL_ANGLE" in params:
        cli_args.append(f"--initial-angle {params['INITIAL_ANGLE']}")
    if "ROTATE_ANGLE" in params:
        cli_args.append(f"--rotation {params['ROTATE_ANGLE']}")
        
    return " ".join(cli_args)
