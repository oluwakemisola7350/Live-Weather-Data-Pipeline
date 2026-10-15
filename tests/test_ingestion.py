from unittest.mock import Mock, patch

import pytest 
import requests

from live_weather_data_platform.ingestion import fetch_weather_data

# Successful API Request
def test_fetch_weather_data_returns_json(): 
    """Successful API requests should return the JSON response."""
    expected_data = {
        "timezone": "America/Sao_Paulo",
        "hourly": {
            "time": ["2026-10-13T00:00"],
            "temperature_2m": [20.2],
        },
    }

    mock_response = Mock()
    mock_response.json.return_value = expected_data

    with patch(
        "live_weather_data_platform.ingestion.requests.get",
        return_value=mock_response,
    ) as mock_get:
        result = fetch_weather_data()

    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()
    assert result == expected_data
    
# HTTP Server Error and Retry Exhaustion
@patch("live_weather_data_platform.ingestion.time.sleep") 
@patch("live_weather_data_platform.ingestion.requests.get")
def test_fetch_weather_data_raises_on_http_error(mock_get, mock_sleep): 
    """A persistent server error should be retried, then reported."""
    mock_response = Mock()
    mock_response.status_code = 503

    http_error = requests.exceptions.HTTPError(
        "503 Service Unavailable",
        response=mock_response,
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    with pytest.raises(
        RuntimeError,
        match="failed after 3 attempts",
    ) as exc_info:
        fetch_weather_data()

    assert exc_info.value.__cause__ is http_error
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2

# Connection Failure After All Retries
@patch("live_weather_data_platform.ingestion.time.sleep") 
@patch("live_weather_data_platform.ingestion.requests.get") 
def test_fetch_weather_data_raises_on_connection_error( mock_get, mock_sleep, ): 
    """Exhausted connection retries should raise a clear error."""
    connection_error = requests.exceptions.ConnectionError(
        "Simulated connection failure"
    )
    mock_get.side_effect = connection_error

    with pytest.raises(
        RuntimeError,
        match="failed after 3 attempts",
    ) as exc_info:
        fetch_weather_data()

    assert isinstance(
        exc_info.value.__cause__,
        requests.exceptions.ConnectionError,
    )
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2

# Successful Retry After Temporary Connection Failure
@patch("live_weather_data_platform.ingestion.time.sleep") 
@patch("live_weather_data_platform.ingestion.requests.get") 
def test_fetch_weather_data_retries_after_connection_error( mock_get, mock_sleep, ):
    """A temporary connection failure should be retried."""
    expected_data = {
        "timezone": "America/Sao_Paulo",
        "hourly": {"time": ["2026-10-13T00:00"]},
    }

    successful_response = Mock()
    successful_response.json.return_value = expected_data

    mock_get.side_effect = [
        requests.exceptions.ConnectionError("Temporary failure"),
        successful_response,
    ]

    result = fetch_weather_data()

    assert result == expected_data
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(2)