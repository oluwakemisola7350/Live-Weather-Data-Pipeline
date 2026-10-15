from pathlib import Path
from unittest.mock import patch

import pandas as pd

from live_weather_data_platform.pipeline import run_weather_pipeline


def test_run_weather_pipeline_returns_validated_dataframe():
    """The pipeline should fetch, save, transform, validate, and return data."""

    raw_response = {
        "hourly": {
            "time": ["2026-10-13T00:00"],
            "temperature_2m": [20.2],
            "relative_humidity_2m": [89],
            "apparent_temperature": [20.5],
            "precipitation": [0.2],
            "rain": [0.2],
            "weather_code": [61],
            "wind_speed_10m": [7.4],
            "wind_direction_10m": [180],
            "wind_gusts_10m": [9.2],
            "surface_pressure": [900.0],
        }
    }

    expected_df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-10-13T00:00"]),
            "temperature_2m": [20.2],
            "relative_humidity_2m": [89],
            "apparent_temperature": [20.5],
            "precipitation": [0.2],
            "rain": [0.2],
            "weather_code": [61],
            "wind_speed_10m": [7.4],
            "wind_direction_10m": [180],
            "wind_gusts_10m": [9.2],
            "surface_pressure": [900.0],
            "location_id": ["brasilia_br"],
            "payload_hash": ["a" * 64],
        }
    )

    expected_path = Path("data/raw/weather_brasilia_test.json")

    with (
        patch(
            "live_weather_data_platform.pipeline.fetch_weather_data",
            return_value=raw_response,
        ) as mock_fetch,

        patch(
            "live_weather_data_platform.pipeline.save_raw_weather_data",
            return_value=expected_path,
        ) as mock_save,

        patch(
            "live_weather_data_platform.pipeline.transform_weather_data",
            return_value=expected_df,
        ) as mock_transform,

        patch(
            "live_weather_data_platform.pipeline.validate_weather_data",
            return_value=True,
        ) as mock_validate,

        patch(
            "live_weather_data_platform.pipeline.update_curated_history",
            return_value=expected_df,
        ) as mock_curated,
    ):
        result_df, result_path = run_weather_pipeline()

    mock_fetch.assert_called_once_with()
    mock_save.assert_called_once_with(raw_response)
    mock_transform.assert_called_once_with(raw_response)
    mock_validate.assert_called_once_with(expected_df)
    mock_curated.assert_called_once_with(expected_df)

    pd.testing.assert_frame_equal(result_df, expected_df)
    assert result_path == expected_path

def test_pipeline_does_not_update_curated_history_when_validation_fails():
    from unittest.mock import Mock

    import pytest

    from live_weather_data_platform import pipeline

    raw_response = {"hourly": {"time": ["2026-10-15T10:00"]}}
    expected_path = Path("data/raw/weather_brasilia_test.json")
    invalid_df = pd.DataFrame({"time": ["invalid"]})

    with (
        patch(
            "live_weather_data_platform.pipeline.fetch_weather_data",
            return_value=raw_response,
        ),
        patch(
            "live_weather_data_platform.pipeline.save_raw_weather_data",
            return_value=expected_path,
        ),
        patch(
            "live_weather_data_platform.pipeline.transform_weather_data",
            return_value=invalid_df,
        ),
        patch(
            "live_weather_data_platform.pipeline.validate_weather_data",
            side_effect=ValueError("Invalid weather data"),
        ),
        patch(
            "live_weather_data_platform.pipeline.update_curated_history"
        ) as mock_curated,
    ):
        with pytest.raises(ValueError, match="Invalid weather data"):
            pipeline.run_weather_pipeline()

    mock_curated.assert_not_called()
