from bs4 import BeautifulSoup
import re
import math

from datetime import datetime, timedelta

def _build_datetime(day_number, time_text):
    if not day_number or not time_text:
        return None

    now = datetime.now()
    hour, minute = map(int, time_text.split(":"))

    day = int(day_number)

    # Date candidate dans le mois courant
    candidate = datetime(
        year=now.year,
        month=now.month,
        day=day,
        hour=hour,
        minute=minute,
    )

    # Si la date calculée est plus de 3 jours dans le passé,
    # c'est probablement le mois suivant.
    if candidate < now - timedelta(days=3):
        if now.month == 12:
            candidate = datetime(
                year=now.year + 1,
                month=1,
                day=day,
                hour=hour,
                minute=minute,
            )
        else:
            candidate = datetime(
                year=now.year,
                month=now.month + 1,
                day=day,
                hour=hour,
                minute=minute,
            )

    return candidate.isoformat()

def _to_int(text):
    if not text:
        return None

    match = re.search(r"-?\d+", text.replace("\xa0", " "))
    return int(match.group(0)) if match else None


def _condition_to_ha(label):
    if not label:
        return "cloudy"

    label = label.lower()

    if "clair" in label or "soleil" in label:
        return "sunny"

    if (
        "peu nuageux" in label
        or "voilé" in label
        or "voile" in label
        or "mitigé" in label
        or "mitige" in label
    ):
        return "partlycloudy"

    if "nuageux" in label or "couvert" in label:
        return "cloudy"

    if "pluie" in label or "averse" in label:
        return "rainy"

    if "orage" in label:
        return "lightning-rainy"

    if "neige" in label:
        return "snowy"

    if "brouillard" in label or "brume" in label:
        return "fog"

    return "cloudy"

def _saturation_vapor_pressure(temp_c):
    if temp_c is None:
        return None
    return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def _vpd_kpa(temp_c, humidity):
    if temp_c is None or humidity is None:
        return None

    es = _saturation_vapor_pressure(temp_c)
    ea = es * (humidity / 100)

    return round(es - ea, 2)


def _parse_latitude(html_text):
    # Exemple : Latitude N 44°04'
    match = re.search(r"Latitude\s+N\s+(\d+)°(\d+)'", html_text)
    if not match:
        return None

    deg = int(match.group(1))
    minutes = int(match.group(2))

    return deg + (minutes / 60)


def _extraterrestrial_radiation(latitude, day_of_year):
    if latitude is None:
        return None

    phi = math.radians(latitude)
    gsc = 0.0820

    dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
    delta = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)

    ws = math.acos(-math.tan(phi) * math.tan(delta))

    ra = (
        (24 * 60 / math.pi)
        * gsc
        * dr
        * (
            ws * math.sin(phi) * math.sin(delta)
            + math.cos(phi) * math.cos(delta) * math.sin(ws)
        )
    )

    return ra


def _etp_hargreaves(tmin, tmax, latitude, date_text):
    if tmin is None or tmax is None or latitude is None or not date_text:
        return None

    try:
        date_obj = datetime.fromisoformat(date_text)
    except ValueError:
        return None

    tmean = (tmin + tmax) / 2
    temp_range = max(tmax - tmin, 0)

    if temp_range == 0:
        return None

    ra = _extraterrestrial_radiation(latitude, date_obj.timetuple().tm_yday)
    if ra is None:
        return None

    etp = 0.0023 * (tmean + 17.8) * math.sqrt(temp_range) * ra

    return round(etp, 1)    


def _parse_row(cells):
    texts = [cell.get_text(" ", strip=True) for cell in cells]

    hour_index = None
    for i, value in enumerate(texts):
        if re.match(r"^\d{2}:\d{2}$", value):
            hour_index = i
            break

    if hour_index is None:
        return None

    if len(cells) <= hour_index + 8:
        return None

    temp_cell = cells[hour_index + 1]
    wind_dir_cell = cells[hour_index + 3]
    wind_speed_cell = cells[hour_index + 4]
    wind_gust_cell = cells[hour_index + 5]
    rain_cell = cells[hour_index + 6]
    humidity_cell = cells[hour_index + 7]
    pressure_cell = cells[hour_index + 8]
    condition_cell = cells[hour_index + 9] if len(cells) > hour_index + 9 else None

    condition_label = None
    wind_bearing = None

    wind_img = wind_dir_cell.find("img")
    if wind_img:
        wind_title = wind_img.get("title") or wind_img.get("alt") or ""
        bearing_match = re.search(r"(\d+)\s*°", wind_title)
        if bearing_match:
            wind_bearing = int(bearing_match.group(1))

    if condition_cell:
        condition_img = condition_cell.find("img")
        if condition_img:
            condition_label = condition_img.get("title") or condition_img.get("alt")

    rain_text = rain_cell.get_text(" ", strip=True)

    return {
        "time": texts[hour_index],
        "temperature": _to_int(temp_cell.get_text(" ", strip=True)),
        "condition": _condition_to_ha(condition_label),
        "condition_label": condition_label,
        "wind_bearing": wind_bearing,
        "wind_speed": _to_int(wind_speed_cell.get_text(" ", strip=True)),
        "wind_gust_speed": _to_int(wind_gust_cell.get_text(" ", strip=True)),
        "precipitation": None if "--" in rain_text else _to_int(rain_text),
        "humidity": _to_int(humidity_cell.get_text(" ", strip=True)),
        "pressure": _to_int(pressure_cell.get_text(" ", strip=True)),
        "vpd": _vpd_kpa(
            _to_int(temp_cell.get_text(" ", strip=True)),
            _to_int(humidity_cell.get_text(" ", strip=True)),
        ),
    }


def _build_daily_forecast(hourly, latitude=None):
    days = {}

    for item in hourly:
        day = item.get("day_number")
        if not day:
            continue

        days.setdefault(day, []).append(item)

    daily = []

    for day, items in days.items():
         
        # Condition pour les journées tronquées avec min max trompeur 
        if len(items) < 4:
            continue

        temperatures = [
            item["temperature"]
            for item in items
            if item.get("temperature") is not None
        ]

        precipitations = [
            item["precipitation"] or 0
            for item in items
        ]

        wind_speeds = [
            item["wind_speed"]
            for item in items
            if item.get("wind_speed") is not None
        ]

        gusts = [
            item["wind_gust_speed"]
            for item in items
            if item.get("wind_gust_speed") is not None
        ]

        # Condition dominante simple : condition de la mi-journée si possible
        midday = None
        for item in items:
            if item.get("time") in ("11:00", "14:00"):
                midday = item
                break

        representative = midday or items[0]

        daily.append({
            "datetime": representative.get("datetime", "")[:10],
            "condition": representative.get("condition"),
            "native_temperature": max(temperatures) if temperatures else None,
            "native_templow": min(temperatures) if temperatures else None,
            "native_precipitation": sum(precipitations),
            "native_wind_speed": max(wind_speeds) if wind_speeds else None,
            "native_wind_gust_speed": max(gusts) if gusts else None,
            "wind_bearing": representative.get("wind_bearing"),
            "humidity": representative.get("humidity"),
            "native_pressure": representative.get("pressure"),
            "etp": _etp_hargreaves(
                min(temperatures) if temperatures else None,
                max(temperatures) if temperatures else None,
                latitude,
                representative.get("datetime", "")[:10],
            ),
        })

    return daily

def _filter_future_hourly(hourly):
    now = datetime.now()
    future = []

    for item in hourly:
        dt = item.get("datetime")
        if not dt:
            continue

        try:
            forecast_time = datetime.fromisoformat(dt)
        except ValueError:
            continue

        if forecast_time >= now:
            future.append(item)

    return future


def parse_forecast(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    latitude = _parse_latitude(page_text)

    forecast_table = None

    candidate_tables = []

    for table in soup.find_all("table"):
        text = table.get_text(" ", strip=True)
        if (
            "Jour" in text
            and "Heure" in text
            and "Temp." in text
            and "Humidité" in text
            and "Pression" in text
            and "Vent km/h" in text
        ):
            candidate_tables.append(table)

    if candidate_tables:
        forecast_table = min(
            candidate_tables,
            key=lambda t: len(t.find_all("tr"))
        )

    if forecast_table is None:
        return {
            "temperature": None,
            "condition": "cloudy",
            "error": "forecast_table_not_found",
            "hourly": [],
        }

    hourly = []
    seen = set()
    current_day_label = None
    current_day_number = None

    for row in forecast_table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 9:
            continue

        texts = [cell.get_text(" ", strip=True) for cell in cells]

        # Détection cellule jour, exemple : "Dim 05"
        first_text = texts[0] if texts else ""

        day_match = re.match(r"^(Lun|Mar|Mer|Jeu|Ven|Sam|Dim)\s+(\d{2})$", first_text)

        if day_match:
            current_day_label = day_match.group(1)
            current_day_number = day_match.group(2)

        parsed = _parse_row(cells)

        if parsed is not None:

            parsed["day_label"] = current_day_label
            parsed["day_number"] = current_day_number

            parsed["datetime"] = _build_datetime(
                current_day_number,
                parsed["time"],
            )

            key = (
                parsed["day_number"],
                parsed["time"],
                parsed["temperature"],
            )

            if key not in seen:
                seen.add(key)
                hourly.append(parsed)
        

    hourly = _filter_future_hourly(hourly)

    if not hourly:
        return {
            "temperature": None,
            "condition": "cloudy",
            "error": "no_future_forecast_found",
            "hourly": [],
            "forecast_hourly": [],
            "forecast_daily": [],
        }

    current = hourly[0]

    return {
        "temperature": current["temperature"],
        "condition": current["condition"],
        "condition_label": current["condition_label"],
        "wind_bearing": current["wind_bearing"],
        "wind_speed": current["wind_speed"],
        "wind_gust_speed": current["wind_gust_speed"],
        "precipitation": current["precipitation"],
        "humidity": current["humidity"],
        "pressure": current["pressure"],
        "vpd": current["vpd"],
        "hourly": hourly,
        "forecast_hourly": [
            {
                "datetime": item["datetime"],
                "condition": item["condition"],
                "native_temperature": item["temperature"],
                "native_pressure": item["pressure"],
                "humidity": item["humidity"],
                "native_wind_speed": item["wind_speed"],
                "native_wind_gust_speed": item["wind_gust_speed"],
                "wind_bearing": item["wind_bearing"],
                "native_precipitation": item["precipitation"],
            }
            for item in hourly
            if item.get("datetime") is not None
        ],
        "forecast_daily": _build_daily_forecast(hourly, latitude),
    }