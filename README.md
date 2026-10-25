# Road Safety Forecasting: Brazilian Highways

Forecasting how many highway accidents with injuries or deaths each of Brazil's 5 macro-regions will have on every day of the next quarter, so regional emergency planners can decide how many ambulances, rescue teams and patrols to have ready on weekends and holidays.

Group project for **Predictive Analytics & Forecasting**, Executive Master in Business Analytics and AI (2026).

## The question

> Each quarter, **1 month before it starts**, forecast the number of accidents with victims (injury or fatal) per region per day for the next quarter.

- **Regions:** Norte, Nordeste, Centro-Oeste, Sudeste, Sul.
- **Target:** accidents with victims per region per day. Days without accidents count as 0.
- **Main use:** weekends and holidays, when planners need the most resources. Models train on all days and are scored mainly on weekends and holidays.

## Data

| Source | What it gives |
|---|---|
| `data/raw/highway_accidents.csv` | 150,000 accident records, 2007–2025: date, location, road characteristics, severity (course dataset) |
| [Open-Meteo historical weather API](https://open-meteo.com/) | daily rain, temperature and humidity for 94 reference cities, used to build the usual weather per region and month |
| [`holidays`](https://pypi.org/project/holidays/) Python package | Brazilian national holidays, Carnival and Corpus Christi |

Coordinates are only available from 2017, and the way accidents were recorded changed in April 2018, so the modelling period runs from **April 2018 to December 2025**.

## Approach

1. **Data quality:** missing and invalid coordinates, implausible km values and duplicates. See [notebooks/data_quality_decisions.md](notebooks/data_quality_decisions.md).
2. **Region:** each accident is assigned to the macro-region of its nearest reference city.
3. **Target table:** accidents with victims per region per day, with 0 for days without accidents.
4. **Features**, all known at the time of the forecast:
   - **Calendar:** weekend, holiday, days to and after a holiday, bridge day, long weekend, school vacation.
   - **Climate:** usual rain, heavy rain, temperature, humidity and fire weather per region and month, from 2008–2018. Not the actual weather on the day, which is unknown 1 month ahead.
   - **History:** average accidents per day before each quarter's cutoff (last quarter, last year, weekends and holidays only, same quarter last year, trend).
5. **Models:** GLM Poisson regression, XGBoost and Random Forest, combined in an ensemble.
6. **Evaluation:** split by time, never randomly. Each quarter is predicted by a model trained only on the days before its cutoff.

| Part | Period |
|---|---|
| Training | 2019 Q3 up to each quarter's cutoff (COVID days left out) |
| Validation | 2023 Q1 – 2024 Q4 |
| Test | 2025 Q1 – 2025 Q4, used once at the end |

## Project structure

```
road_safety_machine_learning/
├── data/
│   ├── raw/highway_accidents.csv        # original dataset
│   └── processed/                       # outputs of notebook 02
│       ├── accidents_region.csv         # one row per accident, with its region
│       ├── holidays_calendar.csv        # one row per day, calendar features
│       ├── climate_features.csv         # one row per region and month
│       ├── history.csv                  # one row per region and quarter
│       └── model_table.csv              # one row per region per day: target + all features
├── notebooks/
│   ├── 02_Data_Understanding_Preparation.ipynb   # data quality, region, target, features
│   ├── 03_Modelling.ipynb                        # evaluation, models, ensemble
│   ├── data_quality_decisions.md
│   └── images/
├── src/
│   └── features.py                      # calendar and region functions shared by the notebooks
├── requirements.txt
└── LICENSE
```

## Getting started

Requires **Python 3.12** or newer (numpy 2.5 needs it).

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

In VS Code or Jupyter, select the `.venv` kernel, then:

1. **`notebooks/02_Data_Understanding_Preparation.ipynb`**: run top to bottom to rebuild `data/processed/`.
2. **`notebooks/03_Modelling.ipynb`**: reads `data/processed/model_table.csv`.

The processed files are committed, so you can start with notebook 03 without running notebook 02.

> **Weather download:** section 6.2 of notebook 02 calls the free Open-Meteo API for 94 cities. Because of the API's request limits, the first download takes about an hour: the code waits on the per-minute limit and stops with a message on the hourly one. Re-run the cell later; finished downloads are cached in `weather_cache.sqlite` (not committed). Only re-run it if you change the weather period, variables or cities.

## Status

- [x] Data understanding and quality decisions
- [x] Region assignment and target table
- [x] Calendar, climate and history features → `model_table.csv`
- [x] Baseline and evaluation set-up
- [x] GLM Poisson, XGBoost, Random Forest
- [x] Ensemble and final test

## Team

- Daniel
- Ivana
- Joao
- Linda

## License

[MIT](LICENSE)
