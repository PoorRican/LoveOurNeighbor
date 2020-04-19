from os import getenv

from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    bucket_name = getenv('AWS_MEDIA_BUCKET_NAME')
    custom_domain = '{}.s3.amazonaws.com'.format(bucket_name)