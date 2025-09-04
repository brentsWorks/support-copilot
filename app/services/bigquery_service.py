from google.cloud import bigquery
from google.oauth2 import service_account
from app.core.config import settings
from typing import List, Dict, Any

class BigQueryService:
	"""Service for handling BigQuery operations."""

	def __init__(self):
		self.client = self._initialize_client()

	def _initialize_client(self) -> bigquery.Client:
		"""Initialize and return a BigQuery client with proper authentication."""
		credentials = service_account.Credentials.from_service_account_file(
			settings.GOOGLE_APPLICATION_CREDENTIALS
		)
		return bigquery.Client(
			project=settings.GOOGLE_CLOUD_PROJECT,
			credentials=credentials
		)
	
	async def test_connection(self) -> Dict[str, str]:
		"""Test the BigQuery connection by running a simple query.
		
		Returns:
			Dict[str, str]: Status of the connection test
		"""
		try:
			query = "SELECT 1"
			query_job = self.client.query(query)
			query_job.result() # Wait for query to complete
			return {"status": "success", "message": "BigQuery connection test successful"}
		except Exception as e:
			return {"status": "error", "message": f"BigQuery connection test failed: {str(e)}"}
		
bigquery_service = BigQueryService()

