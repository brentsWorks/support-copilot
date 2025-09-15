from typing import List, Dict, Any
from google.cloud import bigquery
from app.core.config import settings
from app.services.bigquery_service import BigQueryService
from app.services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)


class RetrievalService:
  """Service for semantic retrieval over ticket embeddings using BigQuery."""

  def __init__(self):
    """Initialize RetrievalService with BigQuery connection and embedding generator."""
    self.bigquery_service = BigQueryService(
      dataset_id=settings.BIGQUERY_DATASET_ID,
      table_id=settings.BIGQUERY_TABLE_ID,  # parity with EmbeddingService
    )
    self.client = self.bigquery_service.client
    self.project_id = settings.GOOGLE_CLOUD_PROJECT
    self.dataset_id = settings.BIGQUERY_DATASET_ID

    # Reuse the embedding service to embed queries
    self.embedding_service = EmbeddingService()

  async def search_similar_tickets(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search over tickets using BigQuery and ML.DISTANCE.

    Steps:
      1) Generate embedding for the input query (768-dim).
      2) Execute the EXACT SQL pattern (distance ascending).
      3) Convert distance -> similarity: similarity = 1 - (distance / 2).
      4) Filter out similarity < 0.5.
      5) Return results (sorted by similarity DESC). Empty list if none.
    """
    if not query or not query.strip():
      return []  # graceful empty
    if limit is None or limit <= 0:
      return []  # defensive guard

    try:
      # Generate query embedding
      query_embedding: List[float] = await self.embedding_service.generate_embedding(query)

      embeddings_table = f"`{self.project_id}.embeddings.ticket_embeddings`"
      tickets_table = f"`{self.project_id}.support_tickets_raw.kaggle_tickets_clean`"

      sql = f"""
      WITH distances AS (
        SELECT
          t.ticket_id,
          t.ticket_subject,
          t.ticket_description,
          t.ticket_resolution,
          ML.DISTANCE(e.embedding_vector, @query_embedding) AS distance
        FROM {embeddings_table} e
        JOIN {tickets_table} t
          ON e.ticket_id = t.ticket_id
      )
      SELECT
        ticket_id,
        ticket_subject,
        ticket_description,
        ticket_resolution,
        1 - (distance / 2) AS similarity_score
      FROM distances
      WHERE 1 - (distance / 2) >= 0.5
      ORDER BY similarity_score DESC
      LIMIT @limit
      """

      job_config = bigquery.QueryJobConfig(
        query_parameters=[
          bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", query_embedding),
          bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
      )

      query_job = self.client.query(sql, job_config=job_config)
      rows = list(query_job.result())

      if not rows:
        return []

      results: List[Dict[str, Any]] = []
      for r in rows:
        results.append({
          "ticket_id": r.ticket_id,
          "ticket_subject": r.ticket_subject,
          "ticket_description": r.ticket_description,
          "ticket_resolution": r.ticket_resolution,
          "similarity_score": float(r.similarity_score),
        })

      return results
    except Exception as e:
      logger.error(f"Retrieval search failed for query='{query[:60]}...': {e}")
      return []  # graceful empty

  def format_rag_context(self, tickets: List[Dict[str, Any]]) -> str:
    """
    Format retrieved tickets into a RAG-ready context string.

    Output:
    Similar Cases:
    Case #{ticket_id}: {subject}
    Issue: {description}
    Resolution: {resolution}
    ---
    [repeat for each ticket]

    Returns empty string if tickets is empty.
    """
    if not tickets:
      return ""

    lines: List[str] = ["Similar Cases:"]
    for t in tickets:
      subject = t.get("ticket_subject") or ""
      description = t.get("ticket_description") or ""
      resolution = t.get("ticket_resolution") or ""

      lines.append(f"Case #{t.get('ticket_id')}: {subject}")
      lines.append(f"Issue: {description}")
      lines.append(f"Resolution: {resolution}")
      lines.append("---")

    out = "\n".join(lines)
    if out.endswith("\n---"):
      out = out[:-4]
    return out


# Create a default instance
retrieval_service = RetrievalService()
