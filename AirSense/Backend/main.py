from fastapi import FastAPI
from pydantic import BaseModel
import requests
import joblib
import numpy as np
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

# ------------------ APP SETUP ------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ LOAD MODEL ------------------
model = joblib.load("model.pkl")

# ------------------ LOAD DATASET ------------------
try:
    df_city = pd.read_csv("city_day.csv") 
except Exception as e:
    print("Error loading dataset:", e)
    df_city = pd.DataFrame()

# ------------------ CLEAN DATA ------------------
if not df_city.empty:
    df_city = df_city.rename(columns={
        "PM2.5": "pm25",
        "PM10": "pm10",
        "NO2": "no2",
        "SO2": "so2",
        "CO": "co",
        "O3": "o3",
    })

    df_city = df_city.dropna(subset=["pm25", "pm10", "no2", "so2", "co", "o3"])


# ------------------ REQUEST MODEL ------------------
class AirInput(BaseModel):
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float
    o3: float


# ------------------ ROUTES ------------------

@app.get("/")
def home():
    return {"message": "API running"}


# 🔥 Predict AQI (ML)
@app.post("/predict")
def predict(data: AirInput):
    try:
        pm25 = data.pm25
        pm10 = data.pm10
        no2 = data.no2
        so2 = data.so2
        co = data.co
        o3 = data.o3

        # Feature engineering
        pm_ratio = pm25 / (pm10 + 1)
        pm_avg = (pm25 + pm10) / 2
        gas_avg = (no2 + so2 + o3) / 3
        gas_total = no2 + so2 + o3

        input_data = np.array([[
            pm25, pm10, no2, so2, co, o3,
            pm_ratio, pm_avg, gas_avg, gas_total
        ]])

        prediction = model.predict(input_data)

        return {"AQI": float(prediction[0])}

    except Exception as e:
        return {"error": str(e)}


#  Get all cities
@app.get("/cities")
def get_cities():
    try:
        cities = df_city["City"].dropna().unique().tolist()
        return {"cities": cities}
    except Exception as e:
        return {"error": str(e)}


@app.get("/city-data/{city}")
def get_city_data(city: str):
    try:
        city = city.strip().lower()  

        city_df = df_city[df_city["City"].str.lower() == city]

        if city_df.empty:
            return {"error": "City not found"}

        latest = city_df.iloc[-1]

        return {
            "pm25": float(latest["pm25"]),
            "pm10": float(latest["pm10"]),
            "no2": float(latest["no2"]),
            "so2": float(latest["so2"]),
            "co": float(latest["co"]),
            "o3": float(latest["o3"]),
        }

    except Exception as e:
        return {"error": str(e)}


# # AQI History
@app.get("/city-history/{city}")
def get_city_history(city: str):
    try:
        city = city.strip().lower()
        city_df = df_city[df_city["City"].str.lower() == city].copy()
        city_df = city_df.dropna(subset=["AQI"])
        city_df = city_df.tail(20)

        if city_df.empty:
            return {"dates": [], "aqi": []}

        return {
            "dates": city_df["Date"].astype(str).tolist(),
            "aqi": [round(float(x), 1) for x in city_df["AQI"].tolist()]
        }
    except Exception as e:
        return {"dates": [], "aqi": []}

#  Live AQI
@app.get("/live-aqi/{city}")
def get_live_aqi(city: str):
    try:
        
        city = city.strip().lower()

        token = "a8c3d45945f5ffd1470f7054a4ef948f2da095ac"

        url = f"https://api.waqi.info/feed/{city}/?token={token}"

        # Adding timeout (avoid hanging)
        response = requests.get(url, timeout=5)

        # Handle bad HTTP response
        if response.status_code != 200:
            return {"error": "Failed to fetch data from AQI API"}

        data = response.json()

        #  Proper error handling
        if data.get("status") != "ok":
            return {"error": "City not found or API limit exceeded"}

        result = data.get("data", {})

        # Safe extraction (no crashes)
        return {
            "city": result.get("city", {}).get("name", city),
            "aqi": result.get("aqi", 0),
            "time": result.get("time", {}).get("s", "N/A"),
            "dominant_pollutant": result.get("dominentpol", "N/A"),
        }

    except requests.exceptions.Timeout:
        return {"error": "AQI API timeout. Try again."}

    except Exception as e:
        return {"error": str(e)}