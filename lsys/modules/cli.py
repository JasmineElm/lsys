import argparse

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="L-System SVG Generator")
    parser.add_argument(
        "--rules",
        type=str,
        help="User-defined L-System rules dictionary (or literal string)",
        default=None,
    )
    parser.add_argument(
        "--axiom",
        type=str,
        help="Axiom for the L-System",
        default="F",
    )
    parser.add_argument(
        "--initial-angle",
        type=float,
        help="Initial angle for the L-System",
        default=None,
    )
    parser.add_argument(
        "--rotation",
        type=float,
        help="Rotation angle for the L-System",
        default=None,
    )
    parser.add_argument(
        "--recursion",
        type=int,
        help="Recursion depth for the L-System (overrides config)",
        default=None,
    )
    parser.add_argument("--title", type=str, help="Title printed in logs")
    parser.add_argument("--paradigm", type=str, choices=["geometric", "stochastic", "extended-geometric", "extended-stochastic"], help="Rule generation mode")
    parser.add_argument("--bleed", type=float, help="Margin padding (in mm)")
    parser.add_argument("--options-per-rule", type=int, help="Rule variations per char for stochastic")
    parser.add_argument("--ppmm", type=float, help="Pixels per mm")
    parser.add_argument("--paper-size", type=float, nargs=2, help="Paper size width and height (mm)")
    parser.add_argument("--background-color", type=str, help="Background color")
    parser.add_argument("--precision", type=int, help="Decimal places to round geometry")
    parser.add_argument("--angle-divisors", type=int, nargs='+', help="Acceptable divisors of 360")
    parser.add_argument("--output-dir", type=str, help="Directory path for SVG files")
    parser.add_argument("--scale", type=float, default=1.2, help="Scale multiplier for length (< >)")
    parser.add_argument("--angle-increment", type=float, default=15.0, help="Angle increment for rotation ( ( ) )")
    parser.add_argument("--weight-increment", type=float, default=1.0, help="Weight increment for line thickness (# !)")
    parser.add_argument("--read", type=str, help="Read an SVG file and output the command line arguments to recreate it", default=None)
    parser.add_argument("--filename", type=str, choices=["datetime", "rules", "unix"], help="Syntax for generating output filenames")
    return parser.parse_args()
