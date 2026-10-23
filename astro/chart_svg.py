"""North-Indian diamond chart as inline SVG for the PDF report.

Fixed-house layout: the Lagna house is always the top-centre diamond;
houses proceed counter-clockwise. Each cell shows the sign number and
the planets in it with their degrees (the Nepali janma-patri style).
"""
from __future__ import annotations

import html

from .names import PLANET_ABBR

# Cell polygons (viewBox 0 0 400 400) and text anchors per house 1..12.
_CELLS = {
    1: ("200,0 300,100 200,200 100,100", 200, 84),
    2: ("0,0 200,0 100,100", 100, 26),
    3: ("0,0 100,100 0,200", 26, 96),
    4: ("0,200 100,100 200,200 100,300", 84, 200),
    5: ("0,200 100,300 0,400", 26, 296),
    6: ("0,400 100,300 200,400", 100, 366),
    7: ("200,400 100,300 200,200 300,300", 200, 308),
    8: ("400,400 300,300 200,400", 300, 366),
    9: ("400,400 400,200 300,300", 374, 296),
    10: ("400,200 300,300 200,200 300,100", 316, 200),
    11: ("400,0 400,200 300,100", 374, 96),
    12: ("400,0 300,100 200,0", 300, 26),
}
_LINES = (
    "M0,0 H400 V400 H0 Z "          # outer square
    "M0,0 L400,400 M400,0 L0,400 "  # diagonals
    "M200,0 L400,200 L200,400 L0,200 Z"  # midpoint diamond
)


def diamond_svg(chart: dict, lagna_sign: int, degrees: dict | None = None,
                title: str = "") -> str:
    """`chart`: {body: sign}; `degrees`: optional {body: degree-in-sign}
    for the Nepali in-cell degree style."""
    by_sign: dict[int, list[str]] = {}
    for body, sign in chart.items():
        if body == "Lagna":
            continue
        label = PLANET_ABBR.get(body, body[:2])
        if degrees and body in degrees:
            label += f" {degrees[body]:.0f}°"
        by_sign.setdefault(sign, []).append(label)
    parts = [
        "<svg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg' "
        "style='width:88mm;height:88mm'>",
        f"<path d='{_LINES}' fill='none' stroke='#6b4f12' stroke-width='1.4'/>",
    ]
    for house in range(1, 13):
        sign = (lagna_sign + house - 1) % 12
        _poly, ax, ay = _CELLS[house]
        bodies = by_sign.get(sign, [])
        if house == 1:
            bodies = ["Asc"] + bodies
        lines = [f"<tspan style='font-size:9px;fill:#8a6d1f'>{sign + 1}</tspan>"]
        for b in bodies:
            lines.append(f"<tspan x='{ax}' dy='13' style='font-size:11.5px;font-weight:600'>{html.escape(b)}</tspan>")
        first_dy = -6 * len(bodies)
        parts.append(
            f"<text x='{ax}' y='{ay}' text-anchor='middle' dy='{first_dy}' "
            f"fill='#1c1a2e'>{''.join(lines)}</text>"
        )
    parts.append("</svg>")
    if title:
        return f"<div class='chart-box'><div class='chart-title'>{html.escape(title)}</div>{''.join(parts)}</div>"
    return "".join(parts)
