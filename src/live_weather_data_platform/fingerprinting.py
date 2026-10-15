import hashlib
import json

FORECAST_VALUE_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "weather_code",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
]

def generate_forecast_hash(record):
    """Generatena stable SHA-256 fingerprint for one forcast record"""
    fingerprint_data = {
        "location_id": record["location_id"],
        "time": record["time"],
        "weather": {
            field: record.get(field)
            for field in FORECAST_VALUE_FIELDS
        },
    }

    canonical_json = json.dumps(
        fingerprint_data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()