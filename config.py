"""Silly things that I needed somewhere to dump."""
import boto3

DBAUTH = {
    "connect_timeout": 1,
    "dbname": "postgres",
    "host": "localhost",
    "password": "supersecret",
    "port": 12345,
    "user": "postgres",
}

S3_BUCKET_NAME = "protect-the-people"


def get_bucket():
    return boto3.resource("s3").Bucket(S3_BUCKET_NAME)
