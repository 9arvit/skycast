from flask import Flask, render_template, request
import requests
import joblib
import plotly.graph_objs as go
import plotly
import json
from datetime import datetime
from collections import defaultdict
from meteostat import Stations, Daily
import pandas as pd
import os

app = Flask(__name__)
API_KEY = "e6984aef959d817858ac45743b40f4a0"
model = joblib.load("weather_model.pkl")

def classify_visibility(meters):
    if meters >= 10000:
        return "Clear"
    elif 4000 <= meters < 10000:
        return "Hazy"
    elif 1000 <= meters < 4000:
        return "Mist"
    else:
        return "Foggy"

def get_weekday_averages(city):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_resp = requests.get(geo_url).json()

        if not geo_resp:
            print(f"No geocode result for city: {city}")
            return {i: 0 for i in range(7)}

        lat = geo_resp[0]["lat"]
        lon = geo_resp[0]["lon"]

        stations = Stations()
        nearby = stations.nearby(lat, lon).fetch(1)

        if nearby.empty:
            print(f"No station found near {city}")
            return {i: 0 for i in range(7)}

        station_id = nearby.index[0]

        start = datetime(datetime.now().year - 10, 1, 1)
        end = datetime(datetime.now().year, 1, 1)

        data = Daily(station_id, start, end)
        df = data.fetch()

        df = df[df["tavg"].notnull()]
        df["weekday"] = df.index.weekday
        weekday_averages = df.groupby("weekday")["tavg"].mean().to_dict()

        for i in range(7):
            if i not in weekday_averages:
                weekday_averages[i] = round(df["tavg"].mean(), 2)

        return weekday_averages

    except Exception as e:
        print("Error fetching Meteostat data:", e)
        return {i: 0 for i in range(7)}

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    prediction = None
    chartJSON = None
    summary = None

    if request.method == "POST":
        city = request.form["city"]
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

        weather_resp = requests.get(weather_url)
        forecast_resp = requests.get(forecast_url)

        if weather_resp.status_code == 200 and forecast_resp.status_code == 200:
            data = weather_resp.json()
            forecast_data = forecast_resp.json()["list"]

            temp = data["main"]["temp"]
            description = data["weather"][0]["description"].title()
            icon = data["weather"][0]["icon"]

            feels_like = data["main"].get("feels_like", 0)
            humidity = data["main"].get("humidity", 0)
            pressure = data["main"].get("pressure", 0)
            wind_speed = data["wind"].get("speed", 0)
            visibility_m = data.get("visibility", 0)
            clouds = data["clouds"].get("all", 0)
            rain = data.get("rain", {}).get("1h", 0)
            snow = data.get("snow", {}).get("1h", 0)

            visibility_label = classify_visibility(visibility_m)
            tomorrow_temp = model.predict([[temp]])[0]
            weekday_averages = get_weekday_averages(city)

            daily_forecast = defaultdict(list)
            for entry in forecast_data:
                date = entry["dt_txt"].split(" ")[0]
                daily_forecast[date].append(entry["main"]["temp"])

            forecast_dates = []
            forecast_temps = []
            forecast_hist = []

            for i, (date, temps) in enumerate(list(daily_forecast.items())[:5]):
                avg_temp = sum(temps) / len(temps)
                forecast_dates.append(date)
                forecast_temps.append(avg_temp)

                day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()
                hist_avg = weekday_averages.get(day_of_week, 0)
                forecast_hist.append(hist_avg)

            tomorrow_date = forecast_dates[1] if len(forecast_dates) > 1 else forecast_dates[0]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=forecast_temps,
                mode='lines+markers',
                name='Forecast',
                line=dict(color='royalblue')
            ))
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=forecast_hist,
                mode='lines+markers',
                name='Historical Avg',
                line=dict(color='green', dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=[tomorrow_date],
                y=[tomorrow_temp],
                mode='markers+text',
                name="Tomorrow's Prediction",
                marker=dict(color='red', size=12),
                text=[f"{round(tomorrow_temp, 1)}°C"],
                textposition='top center'
            ))

            fig.update_layout(
                title=f"5-Day Temperature Forecast for {city.title()}",
                yaxis_title="Temperature (°C)",
                xaxis_title="Date",
                plot_bgcolor="#f7f7f7",
                paper_bgcolor="#f7f7f7",
                font=dict(color="#333"),
                showlegend=True
            )
            chartJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            summary = (
                f"The weather in {city.title()} is currently {description.lower()} "
                f"with a temperature of {temp}°C (feels like {feels_like}°C). "
                f"Humidity is {humidity}%, wind speed is {wind_speed} m/s, and visibility is {visibility_label.lower()}."
            )

            weather = {
                "city": city,
                "temperature": temp,
                "description": description,
                "icon": icon,
                "feels_like": feels_like,
                "humidity": humidity,
                "pressure": pressure,
                "wind_speed": wind_speed,
                "visibility": visibility_label,
                "clouds": clouds,
                "rain": rain,
                "snow": snow
            }
            prediction = round(tomorrow_temp, 2)

        else:
            weather = {"error": "City not found"}

    return render_template("index.html", weather=weather, prediction=prediction, chartJSON=chartJSON, summary=summary)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

