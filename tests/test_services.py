from constructiq.services import cracks, safety


def test_safety_normalize_clamps_and_maps():
    raw = {"safety_score": 140, "overall_status": "bad", "workers_detected": "2",
           "ppe_detection": {"helmet": {"status": "Worn"}, "safety_boots": {"status": "??"}},
           "hazards": [{"description": "a", "severity": "moderate"},
                       {"description": "b", "severity": "severe"}, {"nope": 1}]}
    out = safety.normalize(raw)
    assert out["safety_score"] == 100
    assert out["overall_status"] == "Compliant"
    assert out["ppe_detection"]["helmet"]["status"] == "worn"
    assert out["ppe_detection"]["safety_boots"]["status"] == "not_visible"
    assert [h["severity"] for h in out["hazards"]] == ["Critical", "Medium"]
    assert set(out["ppe_detection"]) == set(safety.PPE_ITEMS)


def test_safety_normalize_handles_garbage():
    out = safety.normalize({"safety_score": "abc", "hazards": None})
    assert out["safety_score"] == 0 and out["overall_status"] == "Non-Compliant"


def test_safety_demo_has_required_keys():
    d = safety.demo_result()
    assert {"safety_score", "overall_status", "ppe_detection", "hazards"} <= set(d)


def test_crack_width_limits():
    assert cracks.width_check(0.1)["within_limit"]
    assert cracks.width_check(0.25)["within_limit"]
    assert not cracks.width_check(0.31)["within_limit"]


def test_crack_normalize_defaults_and_urgency():
    out = cracks.normalize({"defect_type": "spalling", "estimated_width_mm": "1.5", "root_causes": "rebar corrosion"})
    assert out["defect_type"] == "Spalling"
    assert out["estimated_width_mm"] == 1.5
    assert out["urgency"]["level"] == "High"
    assert out["root_causes"] == ["rebar corrosion"]
    assert cracks.normalize({"defect_type": "weird"})["defect_type"] == "Hairline"
