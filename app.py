from flask import Flask, render_template, request
import requests
import joblib
import plotly.graph_objs as go
import plotly
import json
from datetime import datetime
from collections import defaultdict
import os
import sys

app = Flask(__name__)
API_KEY = "e6984aef959d817858ac45743b40f4a0"
model = joblib.load("weather_model.pkl")

def classify_visibility(meters):
    if meters >= 10000:
        return "Clear"
    elif 4000 <= meters < 10000:
        return "Hazy"
    elif 1000 <= meters < 4000:
        return "Misty"
    else:
        return "Foggy"

def get_aqi(lat, lon):
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            aqi = data["list"][0]["main"]["aqi"]
            legend = {
                1: "Good 🌱",
                2: "Fair 🌤️",
                3: "Moderate 😐",
                4: "Poor 😷",
                5: "Very Poor ☠️"
            }
            return legend.get(aqi, "Unknown")
        return "Unavailable"
    except:
        return "Unavailable"

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
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"

        weather_resp = requests.get(weather_url)
        forecast_resp = requests.get(forecast_url)
        geo_resp = requests.get(geo_url).json()

        if weather_resp.status_code == 200 and forecast_resp.status_code == 200 and geo_resp:
            data = weather_resp.json()
            forecast_data = forecast_resp.json()["list"]
            lat, lon = geo_resp[0]["lat"], geo_resp[0]["lon"]

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
            aqi = get_aqi(lat, lon)

            # Prepare forecast data
            daily_forecast = defaultdict(list)
            for entry in forecast_data:
                date = entry["dt_txt"].split(" ")[0]
                daily_forecast[date].append(entry["main"]["temp"])

            forecast_dates = []
            forecast_temps = []

            for i, (date, temps) in enumerate(list(daily_forecast.items())[:5]):
                avg_temp = sum(temps) / len(temps)
                forecast_dates.append(date)
                forecast_temps.append(avg_temp)

            tomorrow_date = forecast_dates[1] if len(forecast_dates) > 1 else forecast_dates[0]

            # Plot graph
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=forecast_temps,
                mode='lines+markers',
                name='Forecast',
                line=dict(color='royalblue')
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
                f"Humidity is {humidity}%, wind speed is {wind_speed} m/s, visibility is {visibility_label.lower()}, "
                f"and air quality is {aqi.lower()}."
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
                "snow": snow,
                "aqi": aqi
            }
            prediction = round(tomorrow_temp, 2)

        else:
            weather = {"error": "City not found"}

    return render_template("index.html", weather=weather, prediction=prediction, chartJSON=chartJSON, summary=summary)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
