"""Construction engineering assistant: Gemini chat plus an offline answer base."""
from __future__ import annotations

SYSTEM_PROMPT = """You are ConstructIQ's site engineering assistant for Indian
construction projects. Answer clearly and briefly, citing IS 456:2000, other IS
codes or OSHA 29 CFR 1926 where relevant. If you are unsure of a clause or
value, say so instead of guessing. You give general guidance only: structural
decisions need a qualified engineer. Current site weather: {weather}."""

SUGGESTIONS = [
    "How long should concrete be cured?",
    "What slump is suitable for heavily reinforced beams?",
    "What cover is needed for moderate exposure?",
    "When can slab formwork be removed?",
]

DISCLAIMER = ("General guidance only. Verify against the current code and confirm "
              "design or safety decisions with a qualified engineer.")

# (keywords, answer). First entry with the most keyword hits wins.
KNOWLEDGE = [
    (["cure", "curing", "moist"],
     "**Curing (IS 456 cl. 13.5):** keep exposed concrete surfaces continuously damp for at least "
     "**7 days** with ordinary Portland cement, and at least **10 days** when mineral admixtures or "
     "blended cements are used. In hot weather start early and keep surfaces from drying out."),
    (["slump", "workability"],
     "**Workability (IS 456 cl. 7.1):** typical slump is about **50-100 mm** for lightly reinforced "
     "slabs, beams, walls and columns, and about **100-150 mm** for heavily reinforced sections. "
     "Do not add water on site to raise slump; use a plasticiser instead."),
    (["cover", "nominal cover"],
     "**Nominal cover (IS 456 Table 16):** about **20 mm** mild, **30 mm** moderate, **45 mm** severe, "
     "**50 mm** very severe and **75 mm** extreme exposure (for general RCC members; columns and fire "
     "ratings can need more). Use spacers to hold cover."),
    (["formwork", "shuttering", "stripping", "strike", "remove"],
     "**Stripping times (IS 456 cl. 11.3, OPC, temperature above about 15 °C):** vertical formwork to "
     "columns, walls and beams 16-24 h; slab soffit 3 days (props refixed); beam soffit 7 days "
     "(props refixed); props to slabs up to 4.5 m span 7 days, over 4.5 m 14 days; props to beams up "
     "to 6 m 14 days, over 6 m 21 days. Longer in cold weather or with blended cement."),
    (["w/c", "water cement", "water-cement", "mix", "m25", "m20", "grade"],
     "**Mix limits (IS 456 Table 5, reinforced concrete):** mild exposure max w/c 0.55 and min cement "
     "300 kg/m³ (M20 minimum); moderate 0.50, 300 kg/m³ (M25); severe 0.45, 320 kg/m³ (M30). "
     "Final mix design should come from a mix-design report and trial cubes."),
    (["cube", "strength", "compressive", "test"],
     "**Cube tests:** 150 mm cubes are cast, cured in water and crushed at **28 days** (7-day results "
     "give an early indication, roughly 65-70% of 28-day strength). Characteristic strength is the "
     "value below which no more than 5% of results fall; acceptance follows IS 456 cl. 16."),
    (["crack", "cracks"],
     "**Cracks (IS 456 cl. 35.3.2):** surface crack width should generally not exceed **0.3 mm** "
     "(0.2 mm in severe exposure). Hairline shrinkage cracks are usually cosmetic; diagonal cracks "
     "near supports, widening cracks or cracks with rust staining need a structural engineer."),
    (["scaffold", "guardrail", "fall"],
     "**Scaffolds (OSHA 1926.451):** fall protection (guardrails or personal fall arrest) is needed "
     "above **10 ft (3 m)**. Top rails sit 38-45 inches high with mid-rails, toeboards where objects "
     "can fall, and a competent person inspects before each shift."),
    (["helmet", "ppe", "boots", "vest", "harness"],
     "**PPE:** industrial safety helmets (IS 2925), safety footwear with toe protection, high-visibility "
     "vests, and full-body harnesses with anchor points for work above about 3 m (OSHA 1926.100, "
     "1926.501). Check condition and fit each shift."),
    (["steel", "rebar", "tmt", "reinforcement", "fe500"],
     "**Reinforcement:** TMT bars to IS 1786 (Fe500 is common). Keep bars clean of loose rust and oil, "
     "tie to the bar-bending schedule, hold cover with spacers, and check lap and anchorage lengths "
     "against the drawings."),
    (["cement", "opc", "ppc"],
     "**Cement:** OPC 43/53 conforms to IS 269 and PPC to IS 1489. Use fresh cement, store off the "
     "ground, dry and stacked no more than about 10 bags high, and use older stock first."),
    (["crane", "wind"],
     "**Cranes and wind:** stop lifting when wind reaches the limit in the manufacturer's load chart, "
     "and stop lifting large-surface loads earlier. Tower cranes should be left free to weathervane. "
     "See IS 875 (Part 3) for wind loads on structures."),
    (["rain", "monsoon"],
     "**Rain:** postpone pours in heavy rain, cover fresh concrete, dewater excavations and keep people "
     "out until re-inspected, and isolate wet electrical supply with working earth-leakage protection."),
]

FALLBACK_NOTE = ("I can answer from my built-in notes on **curing, slump, cover, formwork stripping, mix "
                 "limits, cube tests, cracks, scaffolds, PPE, reinforcement, cement, cranes and rain**. "
                 "Add a Gemini API key in the sidebar for open-ended questions.")


def offline_answer(question: str) -> str:
    text = question.lower()
    best, best_hits = None, 0
    for keywords, answer in KNOWLEDGE:
        hits = sum(1 for k in keywords if k in text)
        if hits > best_hits:
            best, best_hits = answer, hits
    return best or FALLBACK_NOTE
