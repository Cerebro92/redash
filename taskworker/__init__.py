import boto3

from kale import settings

# S3 CLIENT
s3_client = boto3.client('s3')

# SES CLIENT
ses_client = boto3.client('ses')


# s3 GET CLIENT
s3_read_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY
)
