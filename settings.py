import dataclasses
import os


@dataclasses.dataclass
class Config:
    api_root: str = os.getenv('API_ROOT')
    api_key_token = os.getenv('API_KEY_TOKEN')


cfg = Config()
