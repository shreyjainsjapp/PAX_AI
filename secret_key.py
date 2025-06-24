import os
import json
import botocore
import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from config import SECRET_NAME, AWS_REGION_NAME


class AwsSecretManager:
    def __init__(self):
        self._session = botocore.session.get_session()
        self.SECRET_NAME = SECRET_NAME
        self.AWS_REGION_NAME = AWS_REGION_NAME
        self.client = self._session.create_client(
            service_name="secretsmanager",
            region_name=self.AWS_REGION_NAME
        )

    def get_secrets(self) -> bool:
        try:
            cache_config = SecretCacheConfig()
            cache = SecretCache(config=cache_config, client=self.client)
            secret = cache.get_secret_string(self.SECRET_NAME)
            secret = json.loads(secret)

            for key, val in secret.items():
                os.environ[key] = val

        except Exception as e:
            print(e)
            return False
        return True
