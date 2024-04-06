import dataclasses
import os


@dataclasses.dataclass
class Config:
    api_root: str = os.getenv('API_ROOT', 'https://datsedenspace.datsteam.dev')
    api_key_token = os.getenv('API_KEY_TOKEN', '660e0b2768b0d660e0b2768b11')


cfg = Config()
