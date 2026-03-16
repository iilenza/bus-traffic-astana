import pandas as pd
import requests
from geopy.distance import geodesic
from datetime import datetime
import os

POINTS_FILE = "points_astana_top100.csv"
OUTPUT_FILE = "bus_traffic_dataset.csv"

RADIUS_METERS = 1500


def get_bus_positions():

    url = "https://api.citytransport.kz/api/v1/vehicles"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        buses = []

        for v in data:

            lat = v.get("lat")
            lon = v.get("lon")

            if lat and lon:
                buses.append((lat, lon))

        return buses

    except:
        return []


def count_buses(point, buses):

    point_coord = (point["lat"], point["lon"])
    count = 0

    for bus in buses:

        distance = geodesic(point_coord, bus).meters

        if distance <= RADIUS_METERS:
            count += 1

    return count


def get_time_of_day(hour):

    if 6 <= hour < 10:
        return "morning_peak"

    if 10 <= hour < 16:
        return "day"

    if 16 <= hour < 20:
        return "evening_peak"

    if 20 <= hour < 24:
        return "evening"

    return "night"


def collect():

    now = datetime.now()

    day_of_week = now.strftime("%A")
    hour = now.hour
    time_of_day = get_time_of_day(hour)

    points = pd.read_csv(POINTS_FILE)

    buses = get_bus_positions()

    rows = []

    for _, point in points.iterrows():

        bus_count = count_buses(point, buses)

        rows.append({
            "timestamp": now,
            "point_id": point["point_id"],
            "lat": point["lat"],
            "lon": point["lon"],
            "bus_count": bus_count,
            "hour": hour,
            "day_of_week": day_of_week,
            "time_of_day": time_of_day
        })

    df_new = pd.DataFrame(rows)

    if os.path.exists(OUTPUT_FILE):

        df_old = pd.read_csv(OUTPUT_FILE)
        df = pd.concat([df_old, df_new])

    else:
        df = df_new

    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    collect()
