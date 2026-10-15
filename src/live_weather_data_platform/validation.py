import pandas as pd

# Checking Data Quality Independently

def validate_weather_data(weather_df):
    """Validate the structure and basic quality of hourly weather data."""

    required_columns = [
        "time",
        "location_id",
        "payload_hash",
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in weather_df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if weather_df.empty:
        raise ValueError("Weather DataFrame is empty.")

    if weather_df["location_id"].isna().any():
        raise ValueError("Missing location IDs detected.")

    if weather_df["location_id"].astype(str).str.strip().eq("").any():
        raise ValueError("Empty location IDs detected.")

    if weather_df["payload_hash"].isna().any():
        raise ValueError("Missing payload hashes detected.")

    if not weather_df["payload_hash"].astype(str).str.fullmatch(
        r"[0-9a-f]{64}"
    ).all():
        raise ValueError("Invalid payload hashes detected.")

    if weather_df["time"].isna().any():
        raise ValueError("Missing timestamps detected.")

    if weather_df["time"].duplicated().any():
        raise ValueError("Duplicate timestamps detected.")

    if not weather_df["time"].is_monotonic_increasing:
        raise ValueError("Timestamps are not in chronological order.")

    if not weather_df["temperature_2m"].between(-90, 60).all():
        raise ValueError("Temperature outside sanity limits.")

    if not weather_df["relative_humidity_2m"].between(0, 100).all():
        raise ValueError("Humidity outside valid limits.")

    if not weather_df["precipitation"].ge(0).all():
        raise ValueError("Negative precipitation detected.")

    if not weather_df["wind_speed_10m"].ge(0).all():
        raise ValueError("Negative wind speed detected.")

    return True