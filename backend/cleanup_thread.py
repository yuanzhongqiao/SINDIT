from datetime import datetime, timedelta
from distutils import dir_util
from threading import Thread
import time
import shutil
from dateutil import tz
from os import listdir, remove
from os.path import isfile, join
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)
from util.log import logger

DATABASE_EXPORT_DIRECTORY = "database_export"
SAFETY_BACKUPS_DIRECTORY = "safety_backups"
SAFETY_BACKUPS_SUBDIRECTORIES = ["neo4j", "s3", "influx_db"]
MAX_AGE_EXPORT = timedelta(minutes=30)
MAX_AGE_SAFETY_BACKUPS = timedelta(days=1)
DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


def _clean_directory(directory: str, max_age: timedelta):
    try:
        backup_files = [f for f in listdir(directory) if isfile(join(directory, f))]
    except FileNotFoundError:
        logger.info(
            f"Directory scanned for obsolete backups does not (yet) exist: {directory}"
        )
        return
    now = datetime.now().astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )
    for backup_file in backup_files:
        date_time_str = backup_file.split(".")[0]
        try:
            date_time = datetime.strptime(date_time_str, DATETIME_STRF_FORMAT).replace(
                tzinfo=tz.gettz(
                    get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
                )
            )
        except ValueError:
            logger.info(
                f"File exists in backups folder, "
                f"that does not conform to the file-name-format: {backup_file} in {directory}. It was skipped!"
            )
            continue
        age: timedelta = now - date_time
        if age > max_age:
            logger.info(f"Removing backup: {backup_file} with age: {age}")
            remove(join(directory, backup_file))


def _cleanup_thread_loop():
    while True:
        logger.info("Checking for obsolete backups...")
        _clean_directory(directory=DATABASE_EXPORT_DIRECTORY, max_age=MAX_AGE_EXPORT)
        for subdir in SAFETY_BACKUPS_SUBDIRECTORIES:
            _clean_directory(
                directory=SAFETY_BACKUPS_DIRECTORY + "/" + subdir,
                max_age=MAX_AGE_SAFETY_BACKUPS,
            )

        logger.info("Finished checking for obsolete backups.")
        time.sleep(300)


def start_storage_cleanup_thread():
    cleanup_thread = Thread(target=_cleanup_thread_loop)
    cleanup_thread.start()
