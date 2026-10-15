#Live Weather Data Engineering Platform

An end-to-end data engineering project that ingests hourly weather forecast data, validates and transforms it, tracks forecast revisions, and stores raw data in Amazon S3.

### Project Overview

The Live Weather Data Engineering Platform demonstrates core data engineering practices through a reproducible weather data pipeline. It retrieves weather forecasts from the Open-Meteo API, stores the raw API response locally and in Amazon S3, transforms hourly observations into a structured dataset, validates data quality, and incrementally maintains historical forecast versions.

The current implementation focuses on weather forecasts for Brasília, Brazil.

### Architecture
Open-Meteo Weather API
          |
          
     Data Ingestion
          |
          
 Raw JSON Storage ------- Amazon S3 (raw/)
          |
          
 Data Transformation
          |
          
    Data Validation
          |
          
 Incremental Processing
          |
          
 Curated Weather History
 (Local Parquet Storage)

### Key Features

* API ingestion: Retrieves hourly forecast data from Open-Meteo.

* Raw data preservation: Saves timestamped JSON responses locally and uploads copies to Amazon S3.

* Data transformation: Converts nested API responses into a structured pandas DataFrame.

* Data quality validation: Checks required columns, timestamps, and weather-value constraints.

* Forecast version tracking: Uses SHA-256 payload fingerprints to identify distinct forecast versions.

* Incremental processing: Adds new forecast versions to historical storage while avoiding duplicate records.

* Automated testing: Uses pytest to test ingestion, transformation, validation, storage, and pipeline behavior.

* Logging and error handling: Records relevant errors and propagates S3 upload failures.

### Technology Stack

* Python
* pandas
* Open-Meteo API
* Amazon S3
* boto3
* Parquet
* pytest
* uv

### Project Structure

Live-Weather-Data-Platform/
├── data/                         # Generated data (excluded from Git)
├── notebook/
│   └── weather_api_exploration.ipynb
├── src/
│   └── live_weather_data_platform/
│       ├── fingerprinting.py
│       ├── incremental.py
│       ├── ingestion.py
│       ├── main.py
│       ├── pipeline.py
│       ├── storage.py
│       ├── transformation.py
│       └── validation.py
├── tests/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock

### Prerequisites

* Python version specified in .python-version
* uv package manager
* An AWS account and an appropriately permissioned AWS identity for S3 uploads

### Setup

* Clone the repository and navigate into the project directory:
- git clone <https://github.com/oluwakemisola7350>
- cd Live-Weather-Data-Platform

* Install the project dependencies:
- `uv sync`

Configure AWS authentication using your preferred secure method. The current storage implementation uses the `AWS CLI` profile named `Eve` by default and the `eu-north-1` region. You can change these settings through the project configuration or environment variables as supported by the implementation.

* Do not commit AWS credentials, access keys, session tokens, or other secrets to Git.

### Running the Pipeline

* From the project root, run:
- `uv run python -m live_weather_data_platform.main`

- The pipeline retrieves weather data, stores the raw response locally and in S3, transforms and validates the data, and updates the local curated forecast history.

- Generated files are written beneath `data/`, which is excluded from version control.

### Running Tests

* Run the automated test suite:

- `uv run pytest`
- The current test suite contains 32 passing tests.

### Data Storage

* Raw data: Timestamped JSON files are stored locally and uploaded to the configured S3 bucket under the raw/ prefix.

* Curated data: Historical forecast versions are maintained locally in Parquet format under data/curated/.
* The incremental process distinguishes forecast versions using location, forecast timestamp, and payload fingerprint.

### Future Improvements

* Add a scheduled ingestion workflow.
* Store curated data in Amazon S3.
* Add Apache Airflow orchestration.
* Implement automated data-quality reporting.
* Build a weather analytics dashboard.
* Add CI automation for tests and code quality checks.

### Disclaimer
* Weather forecasts may change between API requests. This project is intended for educational and portfolio purposes and is not designed for safety-critical forecasting.

### Author
* Developed as a data engineering portfolio project.

