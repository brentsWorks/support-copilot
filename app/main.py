from fastapi import FastAPI
from app.services.bigquery_service import bigquery_service

app = FastAPI()


@app.get("/test-bigquery")
async def test_bigquery():
    """Test endpoint to verify BigQuery connection."""
    return await bigquery_service.test_connection()
