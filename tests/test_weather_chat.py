import pytest

from constructiq.services import chat, weather


def test_all_conditions_have_advisories():
    for c in weather.CONDITIONS:
        adv = weather.advisory_for(c)
        assert adv["alerts"] and adv["headline"]
        assert all(a["actions"] and a["standard"] for a in adv["alerts"])
    with pytest.raises(ValueError):
        weather.advisory_for("Snow")


def test_required_alerts_present():
    wind = " ".join(a["title"] for a in weather.advisory_for("High Wind")["alerts"]).lower()
    rain = " ".join(a["title"] for a in weather.advisory_for("Heavy Rain")["alerts"]).lower()
    heat = " ".join(a["title"] for a in weather.advisory_for("Extreme Heat")["alerts"]).lower()
    assert "crane" in wind and "electrical" in rain and "curing" in heat


def test_offline_answers_route_by_topic():
    assert "7 days" in chat.offline_answer("How long should I cure concrete?")
    assert "slump" in chat.offline_answer("what slump for beams").lower()
    assert "Table 16" in chat.offline_answer("nominal cover for moderate exposure")
    assert chat.offline_answer("tell me a joke") == chat.FALLBACK_NOTE
