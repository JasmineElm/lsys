import argparse

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="L-System SVG Generator")
    parser.add_argument(
        "--string",
        type=str,
        help="User-defined L-System string to draw directly",
        default=None,
    )
    parser.add_argument(
        "--angle",
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
    parser.add_argument("--paradigm", type=str, choices=["geometric", "stochastic"], help="Rule generation mode")
    parser.add_argument("--bleed", type=float, help="Margin padding (in mm)")
    parser.add_argument("--options-per-rule", type=int, help="Rule variations per char for stochastic")
    parser.add_argument("--ppmm", type=float, help="Pixels per mm")
    parser.add_argument("--paper-size", type=float, nargs=2, help="Paper size width and height (mm)")
    parser.add_argument("--background-color", type=str, help="Background color")
    parser.add_argument("--precision", type=int, help="Decimal places to round geometry")
    parser.add_argument("--angle-divisors", type=int, nargs='+', help="Acceptable divisors of 360")
    parser.add_argument("--output-dir", type=str, help="Directory path for SVG files")
    return parser.parse_args()
