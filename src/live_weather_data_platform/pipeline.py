from live_weather_data_platform.ingestion import fetch_weather_data
from live_weather_data_platform.storage import save_raw_weather_data
from live_weather_data_platform.transformation import transform_weather_data
from live_weather_data_platform.validation import validate_weather_data
from live_weather_data_platform.incremental import update_curated_history

def run_weather_pipeline(): 
    """Run the weather ingestion, transformation, and validation steps."""

    # Fetch raw weather data from the API.
    raw_response = fetch_weather_data()

    # Save the original API response as JSON.
    raw_file_path = save_raw_weather_data(raw_response)

    # Convert the API response into a DataFrame.
    weather_df = transform_weather_data(raw_response)

    # Validate the transformed data.
    validate_weather_data(weather_df)

    # Save only forecast that are new to curated history
    new_versions = update_curated_history(weather_df)

    print(f"New forecast versions added: {len(new_versions)}")

    # Return the validated DataFrame for downstream processing.
    return weather_df, raw_file_path