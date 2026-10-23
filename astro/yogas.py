"""Yoga detection — a curated set of classical combinations whose rules can
be stated exactly. Each hit returns the yoga name and the factual basis."""
from __future__ import annotations

from .charts import dignity, house_of, house_lords, sign_of_house
from .names import PLANETS_7, SIGN_LORDS

MAHAPURUSHA = {
    "Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa",
    "Venus": "Malavya", "Saturn": "Shasha",
}
KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}


def _sign(planets: dict, name: str) -> int:
    return planets[name]["sign"]


def _conjunct(planets: dict, a: str, b: str) -> bool:
    return _sign(planets, a) == _sign(planets, b)


def _mutual_kendra_or_opposition(planets: dict, a: str, b: str, lagna_sign: int) -> bool:
    ha = house_of(_sign(planets, a), _sign(planets, b))
    return ha in KENDRA  # 1 (conjunct), 4, 7 (opposition), 10 from each other


def detect_yogas(planets: dict, lagna_sign: int) -> list[dict]:
    yogas: list[dict] = []
    lords = house_lords(lagna_sign)
    house = {p: house_of(_sign(planets, p), lagna_sign) for p in planets}

    def add(name: str, basis: str):
        yogas.append({"name": name, "basis": basis})

    # Pancha Mahapurusha: graha in kendra from Lagna + own/exalted sign.
    for planet, yoga_name in MAHAPURUSHA.items():
        if house[planet] in KENDRA and dignity(planet, _sign(planets, planet)) in ("own", "exalted"):
            add(
                f"{yoga_name} Yoga (Pancha Mahapurusha)",
                f"{planet} occupies a kendra (house {house[planet]}) in its "
                f"{dignity(planet, _sign(planets, planet))} sign",
            )

    # Gajakesari: Jupiter in kendra from Moon.
    if house_of(_sign(planets, "Jupiter"), _sign(planets, "Moon")) in KENDRA:
        add("Gajakesari Yoga", "Jupiter is in a kendra counted from the Moon")

    # Budha-Aditya: Sun + Mercury together.
    if _conjunct(planets, "Sun", "Mercury"):
        add("Budha-Aditya Yoga", "Sun and Mercury are conjoined in one sign")

    # Chandra-Mangala: Moon-Mars conjunction or mutual kendra.
    if _conjunct(planets, "Moon", "Mars") or _mutual_kendra_or_opposition(planets, "Moon", "Mars", lagna_sign):
        add("Chandra-Mangala Yoga", "Moon and Mars are conjoined or in mutual kendra")

    # Kemadruma: no graha (excl. Sun, nodes) in 2nd/12th/kendra from Moon.
    moon_sign = _sign(planets, "Moon")
    supported = False
    for p in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        rel = house_of(_sign(planets, p), moon_sign)
        if p != "Moon" and (rel in (2, 12) or rel in KENDRA):
            supported = True
    if not supported:
        add("Kemadruma Yoga", "No planet occupies the 2nd, 12th or a kendra from the Moon (isolation of the Moon)")

    # Dhana yoga: conjunctions / exchanges among lords of 2, 5, 9, 11.
    dhana_lords = {2: lords[2], 5: lords[5], 9: lords[9], 11: lords[11]}
    houses_of_lord = {h: house[p] for h, p in dhana_lords.items()}
    keys = list(dhana_lords.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            h1, h2 = keys[i], keys[j]
            p1, p2 = dhana_lords[h1], dhana_lords[h2]
            if p1 == p2:
                add("Dhana Yoga", f"The same planet ({p1}) rules both the {h1}th and {h2}th houses")
            elif _conjunct(planets, p1, p2):
                add("Dhana Yoga", f"{p1} (lord of {h1}) conjoins {p2} (lord of {h2})")
            elif houses_of_lord[h1] == h2 and houses_of_lord[h2] == h1:
                add("Dhana Yoga", f"Exchange (parivartana) between {p1} (lord of {h1}) and {p2} (lord of {h2})")

    # Raj yoga: kendra lord + trikona lord association.
    kendra_lords = {lords[h] for h in KENDRA}
    trikona_lords = {lords[h] for h in TRIKONA}
    for kp in kendra_lords:
        for tp in trikona_lords:
            if kp == tp:
                continue
            if _conjunct(planets, kp, tp):
                add("Raj Yoga", f"Kendra lord {kp} conjoins trikona lord {tp}")
            elif house[kp] == [h for h, p in lords.items() if p == tp][0] and \
                    house[tp] == [h for h, p in lords.items() if p == kp][0]:
                add("Raj Yoga", f"Exchange between kendra lord {kp} and trikona lord {tp}")

    # Vargottama is per-planet (reported in predictions); not a yoga here.
    _ = PLANETS_7, SIGN_LORDS, sign_of_house
    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for y in yogas:
        key = (y["name"], y["basis"])
        if key not in seen:
            seen.add(key)
            unique.append(y)
    return unique
