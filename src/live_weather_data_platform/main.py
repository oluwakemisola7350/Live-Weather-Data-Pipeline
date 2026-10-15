import logging

from pathlib import Path

from live_weather_data_platform.pipeline import run_weather_pipeline

def main(): 
    """Run the weather pipeline and report the result.""" 
    logging.basicConfig( 
        level=logging.INFO, 
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", 
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting the weather data pipeline.")

    weather_df, raw_file_path = run_weather_pipeline()
    logger.info("Raw weather data saved to: %s", raw_file_path)

    logger.info(
        "Pipeline completed successfully. Retrieved %s hourly records.",
        len(weather_df),
    )

    print(weather_df.head())
if __name__ == "__main__": 
    main()