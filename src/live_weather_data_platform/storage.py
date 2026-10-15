import json
import os
from datetime import datetime, timezone
from pathlib import Path
import boto3
import logging


logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" 

AWS_PROFILE = os.getenv("AWS_PROFILE", "Eve")
AWS_REGION = "eu-north-1"
S3_BUCKET = "weather-data-platform-raw-7350"

def save_raw_weather_data(raw_response):
    """Save the original weather API response as a timestamped JSON file."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"weather_brasilia_{timestamp}.json"
    file_path = RAW_DATA_DIR / filename

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(raw_response, file, indent=2, ensure_ascii=False)

    session = boto3.Session(
        profile_name = AWS_PROFILE,
        region_name = AWS_REGION, 
    )

    s3 = session.client("s3")
    s3_key = f"raw/{filename}"
    try:
        s3.upload_file(str(file_path), S3_BUCKET, s3_key)
    except Exception:
        logger.exception("Failed to upload raw weather data to S3: %s", s3_key)
        raise

    print(f"Raw weather data uploaded to s3://{S3_BUCKET}/{s3_key}")

    return file_path