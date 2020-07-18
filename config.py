"""Silly things that I needed somewhere to dump."""
import os
import boto3

DBAUTH = {
    "connect_timeout": 1,
    "dbname": "postgres",
    "host": "localhost",
    "password": "supersecret",
    "port": int(os.environ["IPA_PORT_POSTGRES"]),
    "user": "postgres",
}

S3_BUCKET_NAME = "protect-the-people"


def get_bucket():
    return boto3.resource("s3").Bucket(S3_BUCKET_NAME)
