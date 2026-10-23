"""Calendar and region functions from 02_Data_Understanding_Preparation.ipynb, for use in other notebooks.

In a notebook (running from notebooks/):
    import sys
    sys.path.append(str(ROOT / "src"))
    from features import build_calendar, assign_region
"""
import holidays as pyholidays
import numpy as np
import pandas as pd

# ---- decisions agreed in Task 1 ----
WINDOW_DAYS = 3         # holiday window = holiday date +/- 3 days

REGIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

# Region names used in the notebooks (Portuguese) and the English names used in the weather tables.
REGION_EN = {"Norte": "North", "Nordeste": "Northeast", "Centro-Oeste": "Centre-West",
             "Sudeste": "Southeast", "Sul": "South"}

MAX_ANCHOR_KM = 600   # if a point is further than this from every reference city, we do not trust it

# Optional days from the package that are NOT a full day off, so we skip them
SKIP_HOLIDAYS = ("Ash Wednesday", "Public Servant's Day", "Christmas Eve", "New Year's Eve")

# (city, macro-region, latitude, longitude)
ANCHORS = [
 # Norte
 ("Porto Velho","Norte",-8.76,-63.90),("Ji-Parana","Norte",-10.88,-61.95),("Vilhena","Norte",-12.74,-60.15),
 ("Rio Branco","Norte",-9.97,-67.81),("Manaus","Norte",-3.12,-60.02),("Boa Vista","Norte",2.82,-60.67),
 ("Macapa","Norte",0.03,-51.07),("Belem","Norte",-1.46,-48.50),("Santarem","Norte",-2.44,-54.71),
 ("Maraba","Norte",-5.37,-49.12),("Palmas","Norte",-10.18,-48.33),("Araguaina","Norte",-7.19,-48.21),
 ("Gurupi","Norte",-11.73,-49.07),("Altamira","Norte",-3.20,-52.21),
 # Nordeste
 ("Sao Luis","Nordeste",-2.53,-44.30),("Imperatriz","Nordeste",-5.52,-47.48),("Teresina","Nordeste",-5.09,-42.80),
 ("Fortaleza","Nordeste",-3.73,-38.52),("Juazeiro do Norte","Nordeste",-7.21,-39.32),("Natal","Nordeste",-5.79,-35.21),
 ("Joao Pessoa","Nordeste",-7.12,-34.86),("Campina Grande","Nordeste",-7.23,-35.88),("Recife","Nordeste",-8.05,-34.88),
 ("Petrolina","Nordeste",-9.39,-40.50),("Caruaru","Nordeste",-8.28,-35.98),("Maceio","Nordeste",-9.67,-35.74),
 ("Aracaju","Nordeste",-10.91,-37.07),("Salvador","Nordeste",-12.97,-38.50),("Feira de Santana","Nordeste",-12.27,-38.97),
 ("Vitoria da Conquista","Nordeste",-14.86,-40.84),("Barreiras","Nordeste",-12.15,-44.99),("Ilheus","Nordeste",-14.79,-39.05),
 ("Teixeira de Freitas","Nordeste",-17.54,-39.74),("Bom Jesus da Lapa","Nordeste",-13.25,-43.41),("Picos","Nordeste",-7.08,-41.47),
 # Sudeste
 ("Belo Horizonte","Sudeste",-19.92,-43.94),("Uberlandia","Sudeste",-18.92,-48.28),("Montes Claros","Sudeste",-16.73,-43.86),
 ("Juiz de Fora","Sudeste",-21.76,-43.35),("Governador Valadares","Sudeste",-18.85,-41.95),("Varginha","Sudeste",-21.55,-45.43),
 ("Uberaba","Sudeste",-19.75,-47.93),("Teofilo Otoni","Sudeste",-17.86,-41.51),("Ipatinga","Sudeste",-19.47,-42.54),
 ("Vitoria","Sudeste",-20.32,-40.34),("Linhares","Sudeste",-19.39,-40.07),("Rio de Janeiro","Sudeste",-22.91,-43.17),
 ("Campos","Sudeste",-21.76,-41.32),("Volta Redonda","Sudeste",-22.52,-44.10),("Sao Paulo","Sudeste",-23.55,-46.63),
 ("Campinas","Sudeste",-22.91,-47.06),("Ribeirao Preto","Sudeste",-21.18,-47.81),("Aracatuba","Sudeste",-21.21,-50.43),
 ("Presidente Prudente","Sudeste",-22.12,-51.39),("Sao Jose do Rio Preto","Sudeste",-20.82,-49.38),("Santos","Sudeste",-23.96,-46.33),
 ("Sorocaba","Sudeste",-23.50,-47.45),("Taubate","Sudeste",-23.03,-45.56),("Bauru","Sudeste",-22.31,-49.06),
 # Sul
 ("Curitiba","Sul",-25.43,-49.27),("Cascavel","Sul",-24.96,-53.46),("Londrina","Sul",-23.31,-51.16),
 ("Maringa","Sul",-23.42,-51.94),("Ponta Grossa","Sul",-25.09,-50.16),("Foz do Iguacu","Sul",-25.55,-54.59),
 ("Florianopolis","Sul",-27.60,-48.55),("Chapeco","Sul",-27.10,-52.62),("Joinville","Sul",-26.30,-48.85),
 ("Lages","Sul",-27.82,-50.33),("Porto Alegre","Sul",-30.03,-51.23),("Caxias do Sul","Sul",-29.17,-51.18),
 ("Pelotas","Sul",-31.77,-52.34),("Santa Maria","Sul",-29.69,-53.81),("Passo Fundo","Sul",-28.26,-52.41),
 ("Uruguaiana","Sul",-29.76,-57.09),("Santana do Livramento","Sul",-30.89,-55.53),("Rio Grande","Sul",-32.03,-52.10),
 # Centro-Oeste
 ("Brasilia","Centro-Oeste",-15.78,-47.93),("Goiania","Centro-Oeste",-16.68,-49.25),("Anapolis","Centro-Oeste",-16.33,-48.95),
 ("Rio Verde","Centro-Oeste",-17.80,-50.92),("Catalao","Centro-Oeste",-18.17,-47.94),("Jatai","Centro-Oeste",-17.88,-51.72),
 ("Luziania","Centro-Oeste",-16.25,-47.95),("Campo Grande","Centro-Oeste",-20.46,-54.62),("Dourados","Centro-Oeste",-22.22,-54.81),
 ("Tres Lagoas","Centro-Oeste",-20.75,-51.68),("Corumba","Centro-Oeste",-19.01,-57.65),("Ponta Pora","Centro-Oeste",-22.54,-55.73),
 ("Cuiaba","Centro-Oeste",-15.60,-56.10),("Rondonopolis","Centro-Oeste",-16.47,-54.64),("Sinop","Centro-Oeste",-11.86,-55.50),
 ("Caceres","Centro-Oeste",-16.07,-57.68),("Barra do Garcas","Centro-Oeste",-15.89,-52.26),
]
anchors = pd.DataFrame(ANCHORS, columns=["city", "region", "lat", "lon"])


# ---- region ----

def haversine_km(lat1, lon1, lat2, lon2):
    """Distance in km between two points on the Earth."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


def assign_region(lat, lon):
    """For each point, return: its region, the distance to the nearest city,
    and the extra distance to the nearest city of ANOTHER region (small = near a border)."""
    dist = haversine_km(np.asarray(lat)[:, None], np.asarray(lon)[:, None],
                        anchors.lat.values[None, :], anchors.lon.values[None, :])
    nearest_idx = dist.argmin(axis=1)
    city_regions = anchors.region.to_numpy(dtype=object)
    region = city_regions[nearest_idx]
    nearest_km = dist[np.arange(len(nearest_idx)), nearest_idx]
    other_km = np.where(city_regions[None, :] != region[:, None], dist, np.inf).min(axis=1)
    return region, nearest_km, other_km - nearest_km


# ---- holiday and weekend calendar ----

def get_brazil_holidays(first_year, last_year):
    """Return a Series: date -> holiday name (national holidays + Carnival + Corpus Christi)."""
    found = pyholidays.country_holidays("BR", years=range(first_year, last_year + 1),
                                        categories=("public", "optional"))
    names = pd.Series({pd.Timestamp(d): n for d, n in found.items()}).sort_index()
    return names[~names.str.startswith(SKIP_HOLIDAYS)]


def build_calendar(start, end, window=WINDOW_DAYS):
    dates = pd.date_range(start, end, freq="D")
    cal = pd.DataFrame({"date": dates})

    # --- basic date parts ---
    cal["year"] = dates.year
    cal["quarter"] = dates.quarter
    cal["month"] = dates.month
    cal["day"] = dates.day
    cal["day_of_week"] = dates.day_name()
    cal["is_weekend"] = (dates.dayofweek >= 5).astype(int)      # Saturday or Sunday

    # --- holidays ---
    # We load one extra year before and after, so days at the edge of the calendar
    # (for example 1 January) can still find their nearest holiday.
    hol = get_brazil_holidays(dates.year.min() - 1, dates.year.max() + 1)
    cal["holiday_name"] = cal["date"].map(hol)
    cal["is_holiday"] = cal["holiday_name"].notna().astype(int)

    # --- days before the next holiday and days after the last holiday ---
    hol_days = hol.index.to_numpy().astype("datetime64[D]")
    day = dates.to_numpy().astype("datetime64[D]")

    next_pos = np.searchsorted(hol_days, day, side="left")        # first holiday on or after this day
    prev_pos = np.searchsorted(hol_days, day, side="right") - 1   # last holiday on or before this day
    to_next = (hol_days[next_pos] - day).astype(int)
    since_last = (day - hol_days[prev_pos]).astype(int)

    # 0 = the holiday itself. Empty (NaN) when the holiday is more than `window` days away.
    cal["days_to_holiday"] = pd.Series(to_next).where(lambda s: s <= window).astype("Int64")
    cal["days_after_holiday"] = pd.Series(since_last).where(lambda s: s <= window).astype("Int64")
    cal["is_holiday_window"] = (cal["days_to_holiday"].notna() | cal["days_after_holiday"].notna()).astype(int)

    # --- bridge day ("ponte") ---
    # A working day between a holiday and the weekend. Many people take it off.
    # Monday before a Tuesday holiday, or Friday after a Thursday holiday.
    hol_flag = cal["is_holiday"]
    monday_bridge = (cal["day_of_week"] == "Monday") & (hol_flag.shift(-1, fill_value=0) == 1)
    friday_bridge = (cal["day_of_week"] == "Friday") & (hol_flag.shift(1, fill_value=0) == 1)
    cal["is_bridge_day"] = ((monday_bridge | friday_bridge) & (hol_flag == 0)).astype(int)

    # --- long weekend ---
    # A block of 3 or more days off in a row (weekend, holiday, bridge day)
    # that contains at least one holiday or bridge day. A normal weekend is not a long weekend.
    day_off = (cal["is_weekend"] == 1) | (hol_flag == 1) | (cal["is_bridge_day"] == 1)
    block = (day_off != day_off.shift()).cumsum()                 # new number each time the pattern changes
    block_size = day_off.groupby(block).transform("size")
    has_extra = ((hol_flag == 1) | (cal["is_bridge_day"] == 1)).groupby(block).transform("max")
    cal["is_long_weekend"] = (day_off & (block_size >= 3) & has_extra).astype(int)

    # --- school vacation: July, January, and the second half of December ---
    cal["is_school_vacation"] = (cal["month"].isin([1, 7]) | ((cal["month"] == 12) & (cal["day"] >= 15))).astype(int)

    return cal
