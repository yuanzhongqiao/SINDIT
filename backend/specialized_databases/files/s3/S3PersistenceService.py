""" S3 compatible persistence service """

import json
import boto3
import os
from botocore.client import Config
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from datetime import datetime
from dateutil import tz
from backend.specialized_databases.files.FilesPersistenceService import (
    FilesPersistenceService,
)
from util.file_name_utils import _replace_illegal_characters_from_iri

SAFETY_BACKUP_PATH = "safety_backups/neo4j/"
DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"
EXPORT_INFO_FILE_NAME = "sindit_s3_backup_info.txt"


class S3PersistenceService(FilesPersistenceService):
    """S3 compatible persistence service

    Args:
        FilesPersistenceService (_type_): _description_
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # No exception handling required: If connection unavailable, the setup works anyways
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
        # No exception handling required: If connection unavailable, the calls will wait till it becomes available
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

        # No exception handling required: If connection unavailable, the calls will wait till it becomes available
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": iri},
            ExpiresIn=6000,
        )

    def backup(self, backup_path: str):
        print("Backing up S3...")
        os.makedirs(backup_path)
        backup_file_names = dict()
        self.client.create_bucket(
            Bucket=self.bucket_name
        )  # Idempotent: just to make sure it exists
        for s3_object in self.bucket.objects.all():
            iri = s3_object.key
            file_name = _replace_illegal_characters_from_iri(iri)
            file_path = backup_path + "/" + file_name
            self.client.download_file(self.bucket_name, iri, file_path)
            backup_file_names[iri] = file_name
        # Create info file:
        print("Creating S3 backup info file...")
        info_dict = {
            "bucket_name": self.bucket_name,
            "backup_iri_mappings": backup_file_names,
        }

        info_json = json.dumps(info_dict, indent=4)

        with open(
            backup_path + "/" + EXPORT_INFO_FILE_NAME, "w", encoding="utf-8"
        ) as info_file:
            info_file.write(info_json)

        print("Finished backing up S3.")

    def restore(self, backup_path: str):
        print("Restoring S3...")
        print("Parsing backup...")
        # Parse info file:
        try:
            with open(
                backup_path + "/" + EXPORT_INFO_FILE_NAME, "r", encoding="utf-8"
            ) as info_file:
                info_file_json = info_file.read()
        except FileNotFoundError:
            print("Not a valid backup: s3 info file not found!")
            return

        info_dict = json.loads(info_file_json)
        files: dict = info_dict.get("backup_iri_mappings")
        file_iris = list(files.keys())
        print("Creating a safety backup before overwriting the database...")
        safety_path = SAFETY_BACKUP_PATH + datetime.now().astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        ).strftime(DATETIME_STRF_FORMAT)
        os.makedirs(safety_path)
        self.backup(backup_path=safety_path + "s3")

        # Delete everything:
        print("Deleting everything...")
        try:
            self.bucket.objects.all().delete()
            self.bucket.delete()
        except Exception:
            # Ignore delete exceptions and try import nevertheless (e.g. bucket not existing)
            pass
        self.client.create_bucket(Bucket=self.bucket_name)
        self.bucket = self.resource.Bucket(self.bucket_name)
        print("Deleted everything.")
        print("Restoring...")
        for iri in file_iris:
            file_name = files.get(iri)
            file_path = backup_path + "/" + file_name
            self.bucket.upload_file(file_path, iri)

        print("Finished restoring S3.")
