import pandas as pd
import pytest

from live_weather_data_platform.transformation import (transform_weather_data,)

def sample_weather_response():
    """Return a small, API response for testing."""

    return {
        "hourly": {
            "time": [
                "2026-10-13T00:00",
                "2026-10-13T01:00",
            ],
            "temprature_2m": [20.02, 19.8],
            "relative_humidity_2m": [89, 91],
            "apparent_temperature": [22.1, 21.5],
            "precipitation": [0.2, 0.0],
            "rain": [0.1, 0.0],	
            "weather_code": [51, 3],	
            "wind_speed_10m": [7.4, 6.8],	
            "wind_direction_10m": [18, 25],	
            "wind_gusts_10m": [14.8, 13.2],	
            "surface_pressure": [895.0, 895.2]
        }
    }
def test_transform_returns_dataframe():
    """Transform should return a Pandas DataFrame."""

    result = transform_weather_data(sample_weather_response())

    assert isinstance(result, pd.DataFrame)

def test_transform_preserves_row_count():
    """Transformation should preserve the number of hourly records."""

    result = transform_weather_data(sample_weather_response())
    
    assert len(result) == 2

def test_transform_converts_timestamps():
    """Transformation should convert timestamp strings to datetimes."""

    result = transform_weather_data(sample_weather_response())
        
    assert pd.api.types.is_datetime64_any_dtype(result["time"])

def test_transform_rejects_missing_hourly_section():
    """Transformation should reject responses without hourly data."""

    with pytest.raises(ValueError, match="hourly"):
        transform_weather_data({"timezone": "America/Sao_Paulo"})

def test_transform_weather_data_adds_location_id():
    """Each transformed weather record should identify its location."""

    from live_weather_data_platform.transformation import transform_weather_data

    raw_response = {
        "hourly": {
            "time": [
                "2026-10-13T00:00",
                "2026-10-13T01:00",
            ],
            "temperature_2m": [20.2, 19.8],
            "relative_humidity_2m": [89, 91],
            "precipitation": [0.2, 0.0],
            "wind_speed_10m": [7.4, 6.9],
        }
    }

    weather_df = transform_weather_data(raw_response)

    assert "location_id" in weather_df.columns
    assert weather_df["location_id"].tolist() == [
        "brasilia_br",
        "brasilia_br",
    ]

def test_transform_weather_data_adds_payload_hash():
    """Each transformed forecast record should have a SHA-256 hash."""

    from live_weather_data_platform.transformation import (
        transform_weather_data,
    )

    raw_response = {
        "hourly": {
            "time": ["2026-10-13T00:00", "2026-10-13T01:00"],
            "temperature_2m": [20.2, 19.8],
            "relative_humidity_2m": [89, 91],
            "apparent_temperature": [20.5, 19.6],
            "precipitation": [0.2, 0.0],
            "rain": [0.2, 0.0],
            "weather_code": [61, 3],
            "wind_speed_10m": [7.4, 6.9],
            "wind_direction_10m": [180, 190],
            "wind_gusts_10m": [9.2, 8.1],
            "surface_pressure": [900.0, 901.0],
        }
    }

    weather_df = transform_weather_data(raw_response)

    assert "payload_hash" in weather_df.columns
    assert weather_df["payload_hash"].notna().all()
    assert weather_df["payload_hash"].str.fullmatch(r"[0-9a-f]{64}").all()
    assert weather_df["payload_hash"].nunique() == 2