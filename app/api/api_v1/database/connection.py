from core.config import settings
from sqlalchemy import create_engine


SQLALCHEMY_DATABASE_URL = "postgresql://"+settings.ENDPOINT_DB_USER+":"+settings.ENDPOINT_DB_PASS+"@"+settings.ENDPOINT_DB_HOST+":"+settings.ENDPOINT_DB_PORT+"/"+settings.ENDPOINT_DB_NAME
engine = create_engine(SQLALCHEMY_DATABASE_URL)
    


def query_execute(query):
	with engine.connect() as connection_data:
		dataset_object = connection_data.execute(query)
		return dataset_object