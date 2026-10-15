import pandas as pd
import pytest

from live_weather_data_platform.validation import validate_weather_data

def test_validate_accepts_valid_weather_data(): """Valid weather data should pass validation."""
weather_df = pd.DataFrame(
    {
        "time": pd.to_datetime(
            [
                "2026-10-13T00:00",
                "2026-10-13T01:00",
            ]
        ),
        "location_id": ["brasilia_br", "brasilia_br"],
        "payload_hash": ["a" * 64, "b" * 64],
        "temperature_2m": [20.2, 19.8],
        "relative_humidity_2m": [89, 93],
        "precipitation": [0.2, 0.0],
        "wind_speed_10m": [7.4, 6.8],
    }
)

assert validate_weather_data(weather_df) is True

# Test duplicate Timestamps

def test_validate_rejects_duplicate_timestamps(): """Duplicate timestamps should fail validation."""
weather_df = pd.DataFrame(
    {
        "time": pd.to_datetime(
            [
                "2026-10-13T00:00",
                "2026-10-13T00:00",
            ]
        ),
        "location_id": ["brasilia_br", "brasilia_br"],
        "payload_hash": ["a" * 64, "b" * 64],
        "temperature_2m": [20.2, 19.8],
        "relative_humidity_2m": [89, 93],
        "precipitation": [0.2, 0.0],
        "wind_speed_10m": [7.4, 6.8],
    }
)

with pytest.raises(ValueError, match="Duplicate timestamps"):
    validate_weather_data(weather_df)


# Test Missing Timestamp
def test_validate_rejects_missing_timestamps(): """Missing timestamps should fail validation."""
weather_df = pd.DataFrame(
    {
        "time": pd.to_datetime(
            ["2026-10-13T00:00", None]
        ),
        "location_id": ["brasilia_br", "brasilia_br"],
        "payload_hash": ["a" * 64, "b" * 64],
        "temperature_2m": [20.2, 19.8],
        "relative_humidity_2m": [89, 93],
        "precipitation": [0.2, 0.0],
        "wind_speed_10m": [7.4, 6.8],
    }
)

with pytest.raises(ValueError, match="Missing timestamps"):
    validate_weather_data(weather_df)

# Test Invalid Humidity Values
def test_validate_rejects_invalid_humidity(): """Humidity outside 0–100% should fail validation."""
weather_df = pd.DataFrame(
    {
        "time": pd.to_datetime(
            [
                "2026-10-13T00:00",
                "2026-10-13T01:00",
            ]
        ),
        "location_id": ["brasilia_br", "brasilia_br"],
        "payload_hash": ["a" * 64, "b" * 64],
        "temperature_2m": [20.2, 19.8],
        "relative_humidity_2m": [89, 105],
        "precipitation": [0.2, 0.0],
        "wind_speed_10m": [7.4, 6.8],
    }
)

with pytest.raises(ValueError, match="Humidity outside valid limits"):
    validate_weather_data(weather_df)

# Test Negative Precipitation
def test_validate_rejects_negative_precipitation(): """Negative precipitation should fail validation."""
weather_df = pd.DataFrame(
    {
        "time": pd.to_datetime(
            [
                "2026-10-13T00:00",
                "2026-10-13T01:00",
            ]
        ),
        "location_id": ["brasilia_br", "brasilia_br"],
        "payload_hash": ["a" * 64, "b" * 64],
        "temperature_2m": [20.2, 19.8],
        "relative_humidity_2m": [89, 93],
        "precipitation": [0.2, -0.5],
        "wind_speed_10m": [7.4, 6.8],
    }
)

with pytest.raises(ValueError, match="Negative precipitation detected"):
    validate_weather_data(weather_df)


# Test Negative Wind Speed
def test_validate_rejects_negative_wind_speed(): """Negative wind speed should fail validation."""
weather_df = pd.DataFrame(
    {
        "time": pd.to_datetime(
            [
                "2026-10-13T00:00",
                "2026-10-13T01:00",
            ]
        ),
        "location_id": ["brasilia_br", "brasilia_br"],
        "payload_hash": ["a" * 64, "b" * 64],
        "temperature_2m": [20.2, 19.8],
        "relative_humidity_2m": [89, 93],
        "precipitation": [0.2, 0.0],
        "wind_speed_10m": [7.4, -3.0],
    }
)

with pytest.raises(ValueError, match="Negative wind speed detected"):
    validate_weather_data(weather_df)

def test_validate_rejects_missing_location_id():
    weather_df = pd.DataFrame(
        {
            "time": pd.to_datetime(
                ["2026-10-13T00:00", "2026-10-13T01:00"]
            ),
            "location_id": ["brasilia_br", None],
            "payload_hash": ["a" * 64, "b" * 64],
            "temperature_2m": [20.2, 21.0],
            "relative_humidity_2m": [89, 85],
            "precipitation": [0.2, 0.0],
            "wind_speed_10m": [7.4, 8.1],
        }
    )

    with pytest.raises(ValueError, match="Missing location IDs"):
        validate_weather_data(weather_df)


def test_validate_rejects_invalid_payload_hash():
    weather_df = pd.DataFrame(
        {
            "time": pd.to_datetime(
                ["2026-10-13T00:00", "2026-10-13T01:00"]
            ),
            "location_id": ["brasilia_br", "brasilia_br"],
            "payload_hash": ["not-a-valid-hash", "b" * 64],
            "temperature_2m": [20.2, 21.0],
            "relative_humidity_2m": [89, 85],
            "precipitation": [0.2, 0.0],
            "wind_speed_10m": [7.4, 8.1],
        }
    )

    with pytest.raises(ValueError, match="Invalid payload hashes"):
        validate_weather_data(weather_df)