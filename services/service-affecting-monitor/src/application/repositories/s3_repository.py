import logging
import tempfile

logger = logging.getLogger(__name__)


class S3Repository:
    def __init__(self, s3_client, config):
        self.s3_client = s3_client
        self.config = config

    def upload_file_to_s3(self, file_name, file_content):
        try:
            temp_path = tempfile.NamedTemporaryFile().name

            with open(temp_path, 'w') as tmp_csv_file:
                tmp_csv_file.write(file_content)

            self.s3_client.upload_file(
                temp_path,
                self.config.BANDWIDTH_REPORT_CONFIG["s3_bucket"],
                file_name
            )

            return 200

        except Exception as e:
            logger.exception(f"Error: S3 upload failed {e}")
            return 500
