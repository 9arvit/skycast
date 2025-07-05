# 🌦️ SkyCast - ML-Powered Weather Forecasting App

SkyCast is a sleek and interactive web app that gives **real-time weather updates**, predicts **tomorrow’s temperature using Machine Learning**, and compares it with **historical weather averages**.

🔗 **Live Demo:** [https://skycast-cn2i.onrender.com](https://skycast-cn2i.onrender.com)

---

## 🚀 Features

- 🌐 Get **live weather** for any city using OpenWeatherMap API
- 🤖 Predicts **tomorrow's temperature** using a trained ML model
- 📊 Interactive **Plotly graphs** for:
  - 5-day forecast
  - Tomorrow's prediction
  - Historical average trends
- 🌙 Dark Mode toggle (with local storage)
- 🔍 Clean UI with emoji branding and mobile responsiveness
- 📉 Visibility classification (Clear, Hazy, Foggy)

---

## 🧠 How It Works

- **Flask** serves as the backend framework
- **OpenWeatherMap API** fetches live & 5-day forecast data
- **Scikit-learn** regression model predicts next day’s temperature
- **Meteostat** is used to gather historical temperature data
- **Plotly.js** renders responsive, interactive temperature charts

---

## 💻 Tech Stack

| Layer         | Tools Used                              |
|---------------|------------------------------------------|
| Backend       | Python, Flask                            |
| Machine Learning | scikit-learn, pandas, joblib         |
| Frontend      | HTML, CSS, JavaScript, Plotly            |
| APIs          | OpenWeatherMap, Meteostat                |
| Hosting       | Render                                   |

---

## 📷 Screenshots

> You can replace these links after uploading your images in `static/`

![Homepage](static/screenshot.png)
![Dark Mode](static/darkmode.png)

---

## 🛠️ Local Development Setup

```bash
# Clone the repo
git clone https://github.com/9arvit/skycast.git
cd skycast

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
