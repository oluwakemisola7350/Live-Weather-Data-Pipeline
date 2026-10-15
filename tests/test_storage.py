import json 
from unittest.mock import patch
from live_weather_data_platform.storage import save_raw_weather_data
from unittest.mock import patch

def test_save_raw_weather_data_writes_valid_json(tmp_path): 
    """Raw weather data should be saved as valid JSON."""
    raw_response = { "latitude": -15.78, "timezone": "America/Sao_Paulo", "hourly": { "time": ["2026-10-13T00:00"], "temperature_2m": [20.2], }, }
    with (
        patch(
            "live_weather_data_platform.storage.RAW_DATA_DIR",
            tmp_path,
        ),
        patch(
            "live_weather_data_platform.storage.boto3.Session"
        ) as mock_session,
    ):
        file_path = save_raw_weather_data(raw_response)

    assert file_path.exists()
    assert file_path.parent == tmp_path
    assert file_path.suffix == ".json"
    assert file_path.name.startswith("weather_brasilia_")

    with file_path.open("r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == raw_response

    mock_session.assert_called_once_with(
        profile_name="Eve",
        region_name="eu-north-1",
    )
    mock_session.return_value.client.assert_called_once_with("s3")
    mock_session.return_value.client.return_value.upload_file.assert_called_once_with(
        str(file_path),
        "weather-data-platform-raw-7350",
        f"raw/{file_path.name}",
    )

def test_save_raw_weather_data_raises_when_s3_upload_fails(tmp_path, caplog): 
    """S3 upload failures should be reported to the caller."""
    raw_response = {"latitude": -15.78}
    with (
        patch(
            "live_weather_data_platform.storage.RAW_DATA_DIR",
            tmp_path,
        ),
        patch(
            "live_weather_data_platform.storage.boto3.Session"
        ) as mock_session,
    ):
        
        mock_s3 = mock_session.return_value.client.return_value
        mock_s3.upload_file.side_effect = RuntimeError("S3 upload failed")

        try:
            save_raw_weather_data(raw_response)
        except RuntimeError as error:
            assert str(error) == "S3 upload failed"
        else:
            raise AssertionError("Expected S3 upload failure to be raised")

    assert "Failed to upload raw weather data to S3" in caplog.text
    # The local copy should still exist even when S3 upload fails.
    assert len(list(tmp_path.glob("*.json"))) == 1