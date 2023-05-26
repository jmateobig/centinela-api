import secrets
from typing import List, Union
from dotenv import load_dotenv
import os

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator

load_dotenv(verbose=True)
class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR:str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str =  os.getenv('SERVER_NAME')
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = os.getenv('BACKEND_CORS_ORIGINS1')
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    ENDPOINT_DB_ENGINE: str
    ENDPOINT_DB_NAME: str
    ENDPOINT_DB_USER: str
    ENDPOINT_DB_PASS: str
    ENDPOINT_DB_HOST: str
    ENDPOINT_DB_PORT: str


settings = Settings()