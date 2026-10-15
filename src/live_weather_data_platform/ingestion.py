# Fetch Weather Data with Retry Logic, Purpose: Fetch hourly weather forecast data from the Open-Meteo API.
# How it works:
# 1. Sends an HTTP GET request using the configured API parameters.
# 2. Uses a 30-second timeout to prevent requests from waiting indefinitely.
# 3. Checks the HTTP response status and returns the parsed JSON data
# when the request succeeds.
# 4. Catches request-related exceptions and logs the failed attempt.
# 5. Waits for the configured retry delay before attempting the request again.
# 6. After all configured attempts fail, raises a RuntimeError while
# preserving the original exception as its cause.
# Retry configuration:
# - MAX_RETRIES: Maximum total attempts, including the first request.
# - RETRY_DELAY_SECONDS: Waiting time between failed attempts.
# Current limitation:
# This initial implementation retries all Requests-related exceptions, including HTTP errors that may not be temporary. Retry behavior can be refined to distinguish transient failures from permanent errors.


import logging
import time
import requests

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

logger = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"

LOCATION = {
    "id": "brasilia_br",
    "name": "Brasilia",
    "latitude": -15.7939,
    "longitude": -47.8828,
    "timezone": "America/Sao_Paulo",
}

FORECAST_DAYS = 7

HOURLY_VARIABLES = [
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

REQUEST_PARAMS = {
    "latitude": LOCATION["latitude"],
    "longitude": LOCATION["longitude"],
    "hourly": HOURLY_VARIABLES,
    "forecast_days": FORECAST_DAYS,
    "timezone": LOCATION["timezone"],
}


def fetch_weather_data(): 
    """Fetch weather data, retrying temporary failures.""" 
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                API_URL,
                params=REQUEST_PARAMS,
                timeout=30,
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as error:
            last_error = error

            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            # Retry rate limits and server errors only.
            if status_code != 429 and (
                status_code is None or status_code < 500
            ):
                raise

            logger.warning(
                "Temporary HTTP error (attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as error:
            last_error = error

            logger.warning(
                "Temporary connection failure "
                "(attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

        if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    logger.error(
        "Weather API request failed after %s attempts.",
        MAX_RETRIES,
    )
    raise RuntimeError(
        f"Weather API request failed after {MAX_RETRIES} attempts."
    ) from last_error

    print(LOCATION["id"])