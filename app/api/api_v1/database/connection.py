from core.config import settings
from sqlalchemy import create_engine


SQLALCHEMY_DATABASE_URL = "postgresql://"+settings.ENDPOINT_DB_USER+":"+settings.ENDPOINT_DB_PASS+"@"+settings.ENDPOINT_DB_HOST+":"+settings.ENDPOINT_DB_PORT+"/"+settings.ENDPOINT_DB_NAME
engine = create_engine(SQLALCHEMY_DATABASE_URL)
    

SQLALCHEMY_DATABASE_APP = "postgresql://"+settings.DB_USER+":"+settings.DB_PASS+"@"+settings.DB_HOST+":"+settings.DB_PORT+"/"+settings.DB_NAME
engine_app = create_engine(SQLALCHEMY_DATABASE_APP)

def query_execute(query):
	with engine.connect() as connection_data:
		dataset_object = connection_data.execute(query)
		return dataset_object

def query_execute_app(query):
	with engine_app.connect() as connection_data:
		dataset_object = connection_data.execute(query)
		return dataset_object