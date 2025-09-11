from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
	"""Application settings with BigQuery configuration."""
	# Google Cloud Settings
	GOOGLE_CLOUD_PROJECT: str
	GOOGLE_APPLICATION_CREDENTIALS: str
	BIGQUERY_DATASET_ID: str
	BIGQUERY_TABLE_ID: str
	
	# Embedding Model Settings
	EMBEDDING_MODEL_NAME: str = "text-embedding-004"
	EMBEDDING_TABLE_NAME: str = "ticket_embeddings"

	class Config:
		env_file = ".env"

settings = Settings()