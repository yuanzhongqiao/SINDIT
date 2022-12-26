from datetime import datetime, timedelta
from util.log import logger
from os.path import exists
import yaml

STATUS_FILE_PATH = "./similarity_pipeline_status.yaml"


class SimilarityPipelineStatusManager:

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        SimilarityPipelineStatusManager.__instance = self

        if not exists(STATUS_FILE_PATH):
            self.write_status(
                {
                    "time_series_feature_extraction": {
                        "last_run": None,
                        "active": False,
                        "analyzed_date_time": datetime(
                            year=2022, month=7, day=29, hour=11, minute=0, second=0
                        ),
                        "analyzed_time_range_seconds": timedelta(
                            hours=2
                        ).total_seconds(),
                    },
                    "time_series_dimensionality_reduction": {
                        "last_run": None,
                        "active": False,
                    },
                    "time_series_clustering": {
                        "last_run": None,
                        "active": False,
                    },
                    "text_keyphrase_extraction": {
                        "last_run": None,
                        "active": False,
                    },
                    "cad_analysis": {
                        "last_run": None,
                        "active": False,
                    },
                    "image_analysis": {
                        "last_run": None,
                        "active": False,
                    },
                    "asset_similarity": {
                        "last_run": None,
                        "active": False,
                    },
                }
            )

    def read_status(self):
        with open(STATUS_FILE_PATH, "r") as f:
            return yaml.safe_load(f)

    def write_status(self, data):
        with open(STATUS_FILE_PATH, "w") as f:
            yaml.safe_dump(data=data, stream=f)

    def set_active(self, active: bool, stage: str):
        configuration = self.read_status()
        configuration[stage]["active"] = active
        if active == False:
            configuration[stage]["last_run"] = datetime.now()

        self.write_status(configuration)
