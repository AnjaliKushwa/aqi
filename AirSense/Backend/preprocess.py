import pandas as pd

def load_data():
    df = pd.read_csv("city_day.csv")

    # Rename columns
    df = df.rename(columns={
        "PM2.5": "pm25",
        "PM10": "pm10",
        "NO2": "no2",
        "SO2": "so2",
        "CO": "co",
        "O3": "o3",
        "AQI": "AQI"
    })

    # Keep required columns
    df = df[["pm25", "pm10", "no2", "so2", "co", "o3", "AQI"]]

    # Convert to numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    # Fill missing values (pandas 2.x compatible)
    df = df.ffill()
    df = df.bfill()

    # Remove invalid AQI
    df = df[(df["AQI"] > 0) & (df["AQI"] <= 500)]

    # Feature engineering
    df["pm_ratio"] = df["pm25"] / (df["pm10"] + 1)
    df["pm_avg"] = (df["pm25"] + df["pm10"]) / 2
    df["gas_avg"] = (df["no2"] + df["so2"] + df["o3"]) / 3
    df["gas_total"] = df["no2"] + df["so2"] + df["o3"]

    print("Cleaned Data Shape:", df.shape)

    return df


def split_features_target(df):
    X = df.drop("AQI", axis=1)
    y = df["AQI"]
    return X, y