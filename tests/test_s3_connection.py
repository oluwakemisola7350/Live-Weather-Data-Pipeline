import boto3

AWS_PROFILE = "Eve"
AWS_REGION = "eu-north-1"
BUCKET_NAME = "weather-data-platform-raw-7350"

def main():
    session = boto3.Session(
    profile_name = AWS_PROFILE,
    region_name = AWS_REGION,
    )

    s3 = session.client("s3")
    response = s3.head_bucket(Bucket=BUCKET_NAME)

    print(f"S3 connection successful!")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"HTTP status: {response['ResponseMetadata']['HTTPStatusCode']}")

if __name__ == "__main__":
    main()
