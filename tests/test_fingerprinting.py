from live_weather_data_platform.fingerprinting import (generate_forecast_hash,)

def test_identical_forecasts_produce_identical_hashes():
    """The same forecast content should produce the same fingerprint."""
    record = {
        "location_id": "brasilia_br",
        "time": "2026-10-13T15:00:00",
        "temperature_2m": 24.0,
        "relative_humidity_2m": 70,
        "apparent_temperature": 25.0,
        "precipitation": 0.0,
        "rain": 0.0,
        "weather_code": 1,
        "wind_speed_10m": 8.0,
        "wind_direction_10m": 180,
        "wind_gusts_10m": 12.0,
        "surface_pressure": 900.0,
    }

    first_hash = generate_forecast_hash(record)
    second_hash = generate_forecast_hash(record.copy())

    assert first_hash == second_hash


def test_changed_weather_value_produces_different_hash():
    """A change in a tracked weather value should change the fingerprint."""
    original_record = {
        "location_id": "brasilia_br",
        "time": "2026-10-13T15:00:00",
        "temperature_2m": 24.0,
        "relative_humidity_2m": 70,
        "apparent_temperature": 25.0,
        "precipitation": 0.0,
        "rain": 0.0,
        "weather_code": 1,
        "wind_speed_10m": 8.0,
        "wind_direction_10m": 180,
        "wind_gusts_10m": 12.0,
        "surface_pressure": 900.0,
    }

    changed_record = original_record.copy()
    changed_record["temperature_2m"] = 25.0

    original_hash = generate_forecast_hash(original_record)
    changed_hash = generate_forecast_hash(changed_record)

    assert original_hash != changed_hash