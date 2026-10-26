# ConstructIQ

[![Tests](https://github.com/codeknighthood/constructiq/actions/workflows/ci.yml/badge.svg)](https://github.com/codeknighthood/constructiq/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)

**Multimodal Construction Intelligence Platform** — a Streamlit app that helps site teams audit safety photos,
diagnose cracks, estimate budgets and asset value in INR, and get weather-aware guidance with an engineering chat assistant.
It uses Google Gemini for image and chat analysis and falls back to a clearly labelled demonstration mode when no API key is set.
There is no database, so it deploys to Streamlit Community Cloud in one click.

![ConstructIQ](docs/assets/screenshot.png)

## Features

| Tab | What it does |
| --- | --- |
| **Site Safety & PPE Audit** | Upload a JPG/PNG site photo. Returns `safety_score` (0-100), `overall_status`, a PPE checklist (helmet, high-vis vest, safety boots, harness) and hazards rated Low / Medium / High / Critical with the standard cited (OSHA 29 CFR 1926, IS 456) and a remedy. Download the report as JSON. |
| **Crack Diagnostics** | Upload a concrete or wall photo. Classifies the defect (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling), estimates width in mm, checks it against the IS 456 limit, and lists root causes, repairs and urgency. |
| **Planning & Valuation** | Pick structure type, built-up sq ft, Tier 1/2/3 city and a completion slider. Shows project budget, capex incurred, current market value (INR Lakhs/Crores), cement and steel requirement, a milestone progress bar, and a Pollinations AI prompt for a conceptual 3D rendering. |
| **Daily Site Assistant** | Weather selector (Normal, High Wind, Heavy Rain, Extreme Heat) with alerts such as suspending crane operations, electrical hazard mitigation and concrete curing protocol, plus a multi-turn engineering chatbot. |

The sidebar holds the Gemini API key input, a Live/Demo indicator, feature navigation, an architecture overview and the standards referenced.

## Run locally

```bash
git clone https://github.com/codeknighthood/constructiq.git
cd constructiq
pip install -r requirements.txt
streamlit run app.py
```

Without a key the app runs in demonstration mode. To use Gemini, paste a key into the sidebar
(free keys: <https://aistudio.google.com/app/apikey>), or set it for the whole app with either:

- an environment variable: `GEMINI_API_KEY=...`
- Streamlit secrets (`.streamlit/secrets.toml`): `GEMINI_API_KEY = "..."`

The key is never stored in the code or in the repository.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. On <https://share.streamlit.io>, choose **New app**, select the repo, branch `main` and main file `app.py`.
3. Optional: under **Advanced settings → Secrets**, add `GEMINI_API_KEY = "your-key"` so visitors get live mode.
4. Deploy.

## Project layout

```
app.py                      entry point: page setup, sidebar, four tabs
constructiq/
  config.py                 names, models, severity scale, standards list
  gemini_client.py          Gemini calls, key lookup, JSON parsing, demo fallback
  sidebar.py  styles.py  ui.py
  services/                 safety, cracks, valuation, weather, chat (logic, no UI)
  tabs/                     one render() per tab
tests/                      pytest suite (services + whole-app smoke tests)
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Limits and honesty notes

- Demonstration results are sample data, not an analysis of the uploaded image, and the app says so on screen.
- A photo cannot confirm structural safety or code compliance. Results are decision support; high-severity findings
  need inspection by a qualified engineer.
- Costs, market rates and material quantities are indicative planning assumptions listed in
  `constructiq/services/valuation.py`. Replace them with local data before relying on the numbers.
- Standards and clause references in the alerts and offline answers should be checked against the current
  IS and OSHA documents.
- The 3D rendering comes from the external Pollinations service and may be slow or unavailable.

## Author and credits

- **Author:** Sahil Jasuja ([@sahil007-coder](https://github.com/sahil007-coder))
- **Credit:** this project builds on the earlier group project
  [multimodal-construction-platform](https://github.com/sanidhyaagrawal17/multimodal-construction-platform).
  ConstructIQ was restructured and rebuilt as a Streamlit-only application against the Skill Wallet Capstone Project 1
  brief, with new modules, an INR/IS 456 focus, and its own tests and design, with AI-assisted changes as permitted.

Licensed under the MIT License.
