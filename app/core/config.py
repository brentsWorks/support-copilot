from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
	"""Application settings with BigQuery configuration."""
	# Google Cloud Settings
	GOOGLE_CLOUD_PROJECT: str
	GOOGLE_APPLICATION_CREDENTIALS: str

	class Config:
		env_file = ".env"

settings = Settings()