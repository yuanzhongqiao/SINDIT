""" S3 compatible persistence service """

import boto3
from botocore.client import Config

from backend.specialized_databases.files.FilesPersistenceService import (
    FilesPersistenceService,
)


class S3PersistenceService(FilesPersistenceService):
    """S3 compatible persistence service

    Args:
        FilesPersistenceService (_type_): _description_
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.client = boto3.client(
            "s3",
            endpoint_url=self.host + ":" + self.port,
            aws_access_key_id=self.user,
            aws_secret_access_key=self.key,
            config=Config(signature_version="s3v4"),
            # region_name="eu-north-1",  # ignore region functionality
        )

        self.resource = boto3.resource(
            "s3",
            endpoint_url=self.host + ":" + self.port,
            aws_access_key_id=self.user,
            aws_secret_access_key=self.key,
            config=Config(signature_version="s3v4"),
            # region_name="eu-north-1",  # ignore region functionality
        )

        self.bucket_name = self.group

        self.bucket = self.resource.Bucket(self.bucket_name)

        # Check connection:

    # override
    def stream_file(
        self,
        iri: str,
    ):
        """
        Reads
        :param iri:
        :return:
        :raise IdNotFoundException: if the iri is not found
        """
        file_object = self.bucket.Object(iri)
        response = file_object.get()
        file_stream = response["Body"]
        return file_stream

    # override
    def get_temp_file_url(self, iri: str):
        """Creates a temporary URL to directly access the file from S3 without proxying with FastAPI

        Args:
            iri (str): _description_

        Returns:
            _type_: _description_
        """

        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": iri},
            ExpiresIn=6000,
        )
