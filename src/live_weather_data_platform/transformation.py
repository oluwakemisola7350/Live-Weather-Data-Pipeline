import pandas as pd

from live_weather_data_platform.fingerprinting import(generate_forecast_hash)

from live_weather_data_platform.ingestion import LOCATION

def transform_weather_data(raw_response): 
    """Transform a raw Open-Meteo response into a clean hourly DataFrame."""

    if not isinstance(raw_response, dict):
        raise TypeError("Expected the API response to be a dictionary.")

    if "hourly" not in raw_response:
        raise ValueError("API response is missing the 'hourly' section.")

    hourly_data = raw_response["hourly"]

    if "time" not in hourly_data:
        raise ValueError("Hourly data is missing timestamps.")

    weather_df = pd.DataFrame(hourly_data)

    if weather_df.empty:
        raise ValueError("The API returned no hourly weather records.")

    weather_df["time"] = pd.to_datetime(
        weather_df["time"],
        errors="raise",
    )

    weather_df["location_id"] = LOCATION["id"]

    weather_df["payload_hash"] = weather_df.apply(
        lambda row: generate_forecast_hash(row.to_dict()),
        axis=1,
    )

    if weather_df["time"].isna().any():
        raise ValueError("Missing timestamps detected.")

    if weather_df["time"].duplicated().any():
        raise ValueError("Duplicate timestamps detected.")

    if not weather_df["time"].is_monotonic_increasing:
        raise ValueError("Timestamps are not in chronological order.")

    return weather_df