import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python train_model.py <csv_filename>")
    sys.exit(1)

csv_file = sys.argv[1]
city_key = os.path.splitext(os.path.basename(csv_file))[0].replace("weather_history_", "").strip().lower().replace(" ", "_")

df = pd.read_csv(csv_file)
df['time'] = pd.to_datetime(df['time'])
df['temp'] = df['temperature_2m_mean']
df = df[['time', 'temp']].dropna()
df['next_day_temp'] = df['temp'].shift(-1)
df.dropna(inplace=True)

X = df[['temp']]
y = df['next_day_temp']
model = LinearRegression()
model.fit(X, y)

joblib.dump(model, f"weather_model_{city_key}.pkl")

df['weekday'] = df['time'].dt.weekday
weekday_avg = df.groupby('weekday')['temp'].mean().round(2).to_dict()
joblib.dump(weekday_avg, f"weekday_averages_{city_key}.pkl")

print(f"✅ Trained model and averages saved for {city_key}")
