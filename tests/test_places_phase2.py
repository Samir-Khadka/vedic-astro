"""Phase 2 places: gazetteer size, verified new entries, Nepali names, aliases."""
from astro.places import all_places, get_place, search_places


def test_gazetteer_expanded():
    places = all_places()
    assert len(places) >= 69
    assert len({p["id"] for p in places}) == len(places)
    for p in places:
        assert -90 <= p["lat"] <= 90 and -180 <= p["lon"] <= 180 and p["tz"]


def test_new_places_present():
    assert get_place("gorkha")["lat"] == 28.31884
    assert get_place("nagpur")["country"] == "India"
    assert get_place("abu-dhabi")["tz"] == "Asia/Dubai"
    assert get_place("seoul")["tz"] == "Asia/Seoul"


def test_nepali_names_and_aliases():
    assert get_place("pokhara")["name_ne"] == "पोखरा"
    assert [p["id"] for p in search_places("पोखरा")] == ["pokhara"]
    assert [p["id"] for p in search_places("Mahendranagar")] == ["bhimdatta"]
    assert [p["id"] for p in search_places("Bombay")] == ["mumbai"]
    assert all("name_ne" in p for p in all_places() if p["country"] == "Nepal")
