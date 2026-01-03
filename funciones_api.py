import os
import pandas as pd
import requests
import time

BASE_URL = "https://api.jolpi.ca/ergast/f1"  # URL base 
OUT_DIR = "data/pitstops"                    # carpeta en la que guardar CSV

def crear_dir():
    if not os.path.exists("OUT_DIR"):
        os.makedirs(OUT_DIR, exist_ok=True)

def get_json(url,params={}):
    
    for attempt in range(5):
        time.sleep(0.3)  # Para respetar el limite de llamadas
        resp = requests.get(url, params=params)
        if resp.status_code == 429:
            # espera exponencial antes de reintentar
            wait = 2 ** attempt
            print(f"429 recibido, esperando {wait} s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError("Demasiadas llamadas")

def get_races_for_season(season):
    """
    Devuelve lista de carreras para un año usando /{season}/races.json. [web:4]
    Cada elemento incluye al menos 'round' y 'raceName'.
    """
    url = f"{BASE_URL}/{season}/races.json"
    data = get_json(url)
    if "MRData" in data:
        races = data["MRData"]["RaceTable"]["Races"]
    else:
        races = data["RaceTable"]["Races"]
   
    return [{"season": int(season),"round": int(r["round"]),"raceName": r["raceName"],} for r in races]


def get_all_drivers():
    """
    Descarga todos los pilotos con su driverId y permanentNumber. [web:4]
    Jolpica/Ergast pagina resultados, así que iteramos con ?limit=&offset=.
    """
    drivers = []
    limit = 100  # Es el máximo 
    offset = 0  # Es el default
    while True:
        url = f"{BASE_URL}/drivers.json"
        params = {"limit": limit, "offset": offset}
        data = get_json(url, params)
        mr = data["MRData"]
        batch = mr["DriverTable"]["Drivers"]
        drivers.extend(batch)
        total = int(mr.get("total", len(drivers)))
        offset += limit
        if offset >= total or not batch:
            break

    # mapping driverId -> permanentNumber (puede faltar)
    mapping = {}
    for d in drivers:
        driver_id = d["driverId"]
        number = d.get("permanentNumber") or d.get("code")  # fallback razonable
        mapping[driver_id] = number
    return mapping


def get_pitstops_for_race(season, round_):
    """
    Descarga todos los pitstops de una carrera usando
    /{season}/{round}/pitstops.json. [web:4][web:25]
    """
    url = f"{BASE_URL}/{season}/{round_}/pitstops.json"
    data = get_json(url)
    mr = data["MRData"]
    races = mr["RaceTable"]["Races"]
    if not races:
        return []

    # En Ergast los pitstops están en Races[0]["PitStops"]
    pitstops = races[0].get("PitStops", [])
    return pitstops


def build_pitstop_df_for_race(season, round_, driver_number_map):
    """
    Construye el DataFrame requerido para una carrera:
    columnas: DriverId, DriverNumber, NPitstops, MedianPitStopDuration.
    """
    pitstops = get_pitstops_for_race(season, round_)
    if not pitstops:
        return pd.DataFrame(columns=["DriverId","DriverNumber","NPitstops","MedianPitStopDuration"])

    # Creamos DataFrame bruto de pitstops
    raw = pd.DataFrame(pitstops)

    # En Ergast/Jolpica, driverId suele venir como 'driverId' o dentro de 'driverId'
    # pero para pitstops es 'driverId' (string). [web:25]
    raw["duration"] = pd.to_numeric(raw["duration"], errors="coerce")

    grouped = (raw.groupby("driverId")["duration"].agg(["count", "median"]).reset_index().rename(columns={"driverId": "DriverId","count": "NPitstops","median": "MedianPitStopDuration"}))

    # Añadir DriverNumber usando el mapping driverId -> permanentNumber
    grouped["DriverNumber"] = grouped["DriverId"].map(driver_number_map)

    # Reordenar columnas
    grouped = grouped[["DriverId", "DriverNumber", "NPitstops", "MedianPitStopDuration"]]
    return grouped


if __name__=="__main__":
    crear_dir()
    driver_number_map = get_all_drivers()

    for season in range(2019, 2025):  # 2019–2024 inclusive
        races = get_races_for_season(season)
        print(f"Season {season}: {len(races)} races")

        # Carpeta por temporada si quieres replicar la estructura del apartado 1
        season_dir = os.path.join(OUT_DIR, str(season))
        os.makedirs(season_dir, exist_ok=True)

        for race in races:
            rnd = race["round"]
            race_name = race["raceName"].replace("/", "-")

            df_race = build_pitstop_df_for_race(season, rnd, driver_number_map)

            # Nombre de archivo: p.ej. 2019_round01_pitstops.csv
            filename = f"{season}_round{rnd:02d}_pitstops.csv"
            path = os.path.join(season_dir, filename)

            df_race.to_csv(path, index=False)
            print(f"Saved {path} ({len(df_race)} rows)")

    print("Ha guardado todos correctamente")
