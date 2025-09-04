from google.cloud import bigquery
from google.oauth2 import service_account
from app.core.config import settings
from typing import List, Dict, Any, Optional

class BigQueryService:
	"""Service for handling BigQuery operations."""

	def __init__(self, dataset_id: str, table_id: str):
		"""Initialize BigQuery service with specific dataset and table.
        
        Args:
            dataset_id: The ID of the BigQuery dataset
            table_id: The ID of the table within the dataset
        """
		self.client = self._initialize_client()
		self.dataset_id = dataset_id
		self.table_id = table_id
		self.table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
	
	def _initialize_client(self) -> bigquery.Client:
		"""Initialize and return a BigQuery client with proper authentication."""
		credentials = service_account.Credentials.from_service_account_file(
			settings.GOOGLE_APPLICATION_CREDENTIALS
		)
		return bigquery.Client(
			project=settings.GOOGLE_CLOUD_PROJECT,
			credentials=credentials
		)
	
	async def get_table_schema(self) -> List[Dict[str, Any]]:
		"""Get the schema of the configured table."""
		try:
			table = self.client.get_table(self.table_ref)
			return [
				{
					"name": field.name,
					"type": field.field_type,
					"mode": field.mode
				}
				for field in table.schema
			]
		except Exception as e:
			raise Exception(f"Failed to get table schema: {str(e)}")
	
	async def query_table(self,
					   select_fields: List[str],
					   where_clause: Optional[str] = None,
					   order_by: Optional[str] = None,
					   limit: Optional[int] = None) -> List[Dict[str, Any]]:
		"""Query the configured table with optional filtering and ordering.
		
		Args:
			select_fields: List of fields to select
			where_clause: Optional WHERE clause for filtering
			order_by: Optional ORDER BY clause
			limit: Optional limit on the number of rows returned
		
		Returns:
			List[Dict[str, Any]]: List of query results
		"""
		fields = ", ".join(select_fields)
		query = f"""
			SELECT {fields}
			FROM `{settings.GOOGLE_CLOUD_PROJECT}.{self.dataset_id}.{self.table_id}`
			{f"WHERE {where_clause}" if where_clause else ""}
			LIMIT {limit}
		"""

		try:
			query_job = self.client.query(query)
			return [dict(row) for row in query_job.result()]
		except Exception as e:
			raise Exception(f"Failed to query table: {str(e)}")
	
	async def test_connection(self) -> Dict[str, str]:
		"""Test the BigQuery connection and table access.
		
		Returns:
			Dict[str, str]: Status of the connection test and table access test
		"""
		try:
			self.client.get_table(self.table_ref)
			return {
				"status": "success",
				"message": f"Successfully accessed table {self.dataset_id}.{self.table_id}"
			}
		except Exception as e:
			return {"status": "error", "message": f"Connection or table access failed: {str(e)}"}
		
bigquery_service = BigQueryService(
	dataset_id=settings.BIGQUERY_DATASET_ID,
	table_id=settings.BIGQUERY_TABLE_ID
)

