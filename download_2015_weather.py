import requests
import pandas as pd

cities = {
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Nottingham": {"lat": 52.9548, "lon": -1.1581}
}

start, end = "2015-01-01", "2015-12-31"
daily_vars = "temperature_2m_max,temperature_2m_min,temperature_2m_mean"
url = "https://archive-api.open-meteo.com/v1/archive"

for city, coords in cities.items():
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": start,
        "end_date": end,
        "daily": daily_vars,
        "timezone": "auto",
        "temperature_unit": "celsius"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()["daily"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df.to_csv(f"weather_history_{city.lower()}.csv", index=False)
    print(f"{city}: saved {len(df)} rows")

