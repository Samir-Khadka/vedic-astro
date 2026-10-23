"""Jaimini building blocks: sign (rasi) aspects, the stronger co-lord rule
for Scorpio/Aquarius, and bhava arudhas (Arudha Lagna, Upapada Lagna).

Conventions follow the Jaimini Sutras as systematised by K. N. Rao and
P. V. R. Narasimha Rao (the rules Jagannatha Hora implements):

* Rasi drishti (sign aspects): a movable sign aspects every fixed sign
  except the fixed sign next to it; a fixed sign aspects every movable
  sign except the movable sign next to it; a dual sign aspects every
  other dual sign.
* Scorpio has two lords (Mars and Ketu) and Aquarius two (Saturn and
  Rahu). The stronger one — used for arudhas and Chara dasha — is found
  by the classical ladder: (0) if exactly one co-lord sits in the sign
  itself, the OTHER is stronger; (1) the one joined by more planets;
  (2) the one more associated with Jupiter, Mercury and its dispositor
  (by conjunction or rasi aspect); (3) an exalted planet beats a
  non-exalted one; (4) the one in the stronger sign order
  dual > fixed > movable; (5) the one with the higher degree in sign.
* Bhava arudha of a house: count the signs from the house sign to its
  lord (inclusive), then count the same number from the lord's sign.
  Exception: an arudha may not fall in the house sign itself or in the
  7th from it; when it does, take the sign 10th from the computed
  arudha (the standard JHora/PVR resolution of the sutra exception).
"""
from __future__ import annotations

from .charts import dignity
from .names import SIGN_LORDS

# sign index % 3: 0 movable, 1 fixed, 2 dual
def _modality(sign: int) -> int:
    return sign % 3


def rasi_aspects(sign: int) -> list[int]:
    """Signs aspected (rasi drishti) by `sign`."""
    mod = _modality(sign)
    if mod == 2:  # dual aspects all other dual signs
        return [s for s in range(12) if _modality(s) == 2 and s != sign]
    target_mod = 1 if mod == 0 else 0  # movable <-> fixed
    # The adjacent target sign is excluded: for a movable sign that is
    # the fixed sign right after it (Aries does not aspect Taurus); for
    # a fixed sign it is the movable sign right before it (Taurus does
    # not aspect Aries).
    adjacent = (sign + 1) % 12 if mod == 0 else (sign - 1) % 12
    return [s for s in range(12)
            if _modality(s) == target_mod and s != adjacent]


def _sign_of(planets: dict, planet: str) -> int:
    return planets[planet]["sign"]


def stronger_co_lord(planets: dict, sign: int) -> str:
    """Stronger lord of a dual-lordship sign (7=Scorpio: Mars/Ketu,
    10=Aquarius: Saturn/Rahu). For other signs returns the plain lord."""
    if sign == 7:
        graha, node = "Mars", "Ketu"
    elif sign == 10:
        graha, node = "Saturn", "Rahu"
    else:
        return SIGN_LORDS[sign]

    g_sign, n_sign = _sign_of(planets, graha), _sign_of(planets, node)
    # (0) Exactly one co-lord in the sign itself -> the other is stronger.
    if (g_sign == sign) != (n_sign == sign):
        return node if g_sign == sign else graha
    # (1) Joined by more planets (all 9 grahas counted, self excluded).
    def co_count(planet: str, its_sign: int) -> int:
        return sum(1 for q in planets if q != planet and planets[q]["sign"] == its_sign)
    gc, nc = co_count(graha, g_sign), co_count(node, n_sign)
    if gc != nc:
        return graha if gc > nc else node
    # (2) Association with Jupiter / Mercury / own dispositor, by
    # conjunction or rasi aspect on the planet's sign.
    def assoc_count(planet: str, its_sign: int) -> int:
        watched = {"Jupiter", "Mercury", SIGN_LORDS[its_sign]}
        total = 0
        for w in watched:
            if w == planet:
                continue
            w_sign = _sign_of(planets, w)
            if w_sign == its_sign or its_sign in rasi_aspects(w_sign):
                total += 1
        return total
    ga, na = assoc_count(graha, g_sign), assoc_count(node, n_sign)
    if ga != na:
        return graha if ga > na else node
    # (3) Exalted beats non-exalted (nodes carry no dignity in our table,
    # so this can only fire for the graha).
    if dignity(graha, g_sign) == "exalted":
        return graha
    # (4) Sign modality strength: dual (3) > fixed (2) > movable (1).
    def mod_strength(s: int) -> int:
        return {2: 3, 1: 2, 0: 1}[_modality(s)]
    gs, ns = mod_strength(g_sign), mod_strength(n_sign)
    if gs != ns:
        return graha if gs > ns else node
    # (5) Higher degree in sign wins.
    return graha if planets[graha]["degree_in_sign"] >= planets[node]["degree_in_sign"] else node


def sign_lord_jaimini(planets: dict, sign: int) -> str:
    """Lord of a sign under Jaimini co-lordship (stronger of the two for
    Scorpio/Aquarius); the plain Parashari lord otherwise."""
    if sign in (7, 10):
        return stronger_co_lord(planets, sign)
    return SIGN_LORDS[sign]


def _count_rasis(a: int, b: int) -> int:
    """Inclusive zodiacal count of signs from a to b (1..12)."""
    return (b - a) % 12 + 1


def bhava_arudha(planets: dict, base_sign: int) -> tuple[int, dict]:
    """Arudha sign of the house whose sign is `base_sign`, plus the
    working (lord used, count, whether the exception fired)."""
    lord = sign_lord_jaimini(planets, base_sign)
    lord_sign = _sign_of(planets, lord)
    count = _count_rasis(base_sign, lord_sign)
    arudha = (lord_sign + count - 1) % 12
    exception = False
    if _count_rasis(base_sign, arudha) - 1 in (0, 6):
        arudha = (arudha + 9) % 12
        exception = True
    return arudha, {"lord": lord, "lord_sign": lord_sign, "count": count,
                    "exception": exception}


def special_lagnas(planets: dict, lagna_sign: int) -> dict:
    """Arudha Lagna (from the Lagna), Upapada Lagna (from the 12th sign)
    and the Chandra Lagna sign (the Moon's sign read as a lagna)."""
    al, al_work = bhava_arudha(planets, lagna_sign)
    twelfth_sign = (lagna_sign + 11) % 12
    ul, ul_work = bhava_arudha(planets, twelfth_sign)
    return {
        "arudha_lagna": {**al_work, "sign": al},
        "upapada": {**ul_work, "sign": ul, "base_sign": twelfth_sign},
        "chandra_lagna_sign": planets["Moon"]["sign"],
    }
