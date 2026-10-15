from unittest.mock import patch

import pandas as pd

from live_weather_data_platform.incremental import load_curated_history

from live_weather_data_platform.incremental import (
    identify_new_forecast_versions,
)

from live_weather_data_platform.incremental import (
    identify_new_forecast_versions,
    load_curated_history,
    save_curated_history,
)

from live_weather_data_platform import incremental

from live_weather_data_platform import incremental


def test_load_curated_history_returns_empty_dataframe_when_file_missing():
    """Return an empty DataFrame when no curated history exists."""

    with patch(
        "live_weather_data_platform.incremental.Path.exists",
        return_value=False,
    ):
        result = load_curated_history()

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_identify_new_forecast_versions_returns_all_records_for_empty_history():
    """All incoming records are new when history is empty."""

    incoming_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": pd.to_datetime(["2026-10-13T10:00"]),
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    history_df = pd.DataFrame()

    result = identify_new_forecast_versions(incoming_df, history_df)

    pd.testing.assert_frame_equal(result, incoming_df)


def test_identify_new_forecast_versions_excludes_unchanged_records():
    """An already stored forecast version is not added again."""

    incoming_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": pd.to_datetime(["2026-10-13T10:00"]),
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    history_df = incoming_df.copy()

    result = identify_new_forecast_versions(incoming_df, history_df)

    assert result.empty


def test_identify_new_forecast_versions_keeps_changed_forecasts():
    """A changed hash creates a new version for the same forecast time."""

    incoming_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": pd.to_datetime(["2026-10-13T10:00"]),
            "payload_hash": ["b" * 64],
            "temperature_2m": [27.0],
        }
    )

    history_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": pd.to_datetime(["2026-10-13T10:00"]),
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    result = identify_new_forecast_versions(incoming_df, history_df)

    assert len(result) == 1
    assert result.iloc[0]["payload_hash"] == "b" * 64
    assert result.iloc[0]["temperature_2m"] == 27.0

def test_save_curated_history_writes_parquet_file(tmp_path):
    """Save curated history as Parquet and verify its contents."""

    history_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": pd.to_datetime(["2026-10-13T10:00"]),
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    parquet_file = tmp_path / "weather_history.parquet"

    with (
        patch(
            "live_weather_data_platform.incremental.CURATED_DATA_DIR",
            tmp_path,
        ),
        patch(
            "live_weather_data_platform.incremental.CURATED_FILE",
            parquet_file,
        ),
    ):
        save_curated_history(history_df)

    assert parquet_file.exists()

    saved_df = pd.read_parquet(parquet_file)

    pd.testing.assert_frame_equal(saved_df, history_df)

def test_update_curated_history_saves_new_versions(tmp_path): 

    incoming_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": [pd.Timestamp("2026-10-15 10:00:00")],
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    history_file = tmp_path / "weather_history.parquet"

    incremental.CURATED_DATA_DIR = tmp_path
    incremental.CURATED_FILE = history_file

    new_versions = incremental.update_curated_history(incoming_df)

    assert len(new_versions) == 1
    assert history_file.exists()

    saved_history = pd.read_parquet(history_file)

    assert len(saved_history) == 1
    assert saved_history.iloc[0]["temperature_2m"] == 25.0

def test_update_curated_history_does_not_duplicate_unchanged_versions( tmp_path, ):

    incoming_df = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": [pd.Timestamp("2026-10-15 10:00:00")],
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    history_file = tmp_path / "weather_history.parquet"

    incremental.CURATED_DATA_DIR = tmp_path
    incremental.CURATED_FILE = history_file

    first_run = incremental.update_curated_history(incoming_df)
    second_run = incremental.update_curated_history(incoming_df)

    saved_history = pd.read_parquet(history_file)

    assert len(first_run) == 1
    assert second_run.empty
    assert len(saved_history) == 1

def test_update_curated_history_keeps_revised_forecast_versions(
    tmp_path,
):
    import pandas as pd

    from live_weather_data_platform import incremental

    history_file = tmp_path / "weather_history.parquet"

    incremental.CURATED_DATA_DIR = tmp_path
    incremental.CURATED_FILE = history_file

    original_forecast = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": [pd.Timestamp("2026-10-15 10:00:00")],
            "payload_hash": ["a" * 64],
            "temperature_2m": [25.0],
        }
    )

    revised_forecast = pd.DataFrame(
        {
            "location_id": ["brasilia_br"],
            "time": [pd.Timestamp("2026-10-15 10:00:00")],
            "payload_hash": ["b" * 64],
            "temperature_2m": [27.0],
        }
    )

    incremental.update_curated_history(original_forecast)
    added_versions = incremental.update_curated_history(
        revised_forecast
    )

    saved_history = pd.read_parquet(history_file)

    assert len(added_versions) == 1
    assert len(saved_history) == 2
    assert set(saved_history["temperature_2m"]) == {25.0, 27.0}
    assert saved_history["payload_hash"].nunique() == 2