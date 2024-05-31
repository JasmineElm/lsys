"""
    This module contains functions used in the body of svg files
"""

from helpers import svg


def line(start_xy, end_xy, addnl_styles):
    """return a line from start_xy to end_xy"""
    styles = svg.dict_to_tags(addnl_styles)
    linedef = f"<line x1='{start_xy[0]}' y1='{start_xy[1]}' "
    linedef += f" x2='{end_xy[0]}' y2='{end_xy[1]}' {styles} />"
    return linedef
