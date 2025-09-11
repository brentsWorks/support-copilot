"""
EmbeddingService class for generating text embeddings using BigQuery ML's native functions.
"""

from google.cloud import bigquery
s
from app.core.config import settings
from app.services.bigquery_service import BigQueryService
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using BigQuery ML's native embedding functions."""

    def __init__(self):
        """Initialize EmbeddingService with BigQuery connection."""
        self.bigquery_service = BigQueryService(
            dataset_id=settings.BIGQUERY_DATASET_ID,
            table_id=settings.BIGQUERY_TABLE_ID
        )
        self.client = self.bigquery_service.client
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.dataset_id = settings.BIGQUERY_DATASET_ID

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate 768-dimensional embedding for text using text-embedding-004 model.
        
        Args:
            text: The text to generate embedding for
            
        Returns:
            List[float]: 768-dimensional embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty or None")
            
        # Escape text for SQL - handle quotes and newlines
        escaped_text = text.replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
        
        query = f"""
        SELECT ml_generate_embedding_result AS embedding
        FROM ML.GENERATE_EMBEDDING(
            MODEL `{self.project_id}.ml_playground.text_embed_model`,
            (SELECT '{escaped_text}' AS content),
            STRUCT(TRUE AS flatten_json_output)
        )
        """
        
        try:
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            if not results:
                raise Exception("No embedding result returned")
                
            embedding_result = results[0].embedding
            
            # Validate that we got a 768-dimensional vector
            if not isinstance(embedding_result, list) or len(embedding_result) != 768:
                raise Exception(f"Expected 768-dimensional vector, got {len(embedding_result) if isinstance(embedding_result, list) else 'non-list'}")
                
            return embedding_result
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")

    def prepare_ticket_text(self, ticket: Dict[str, Any]) -> str:
        """Combine ticket fields into formatted text for embedding generation.
        
        Args:
            ticket: Dictionary containing ticket information with keys:
                   - subject/ticket_subject: Ticket subject line
                   - description/ticket_description: Issue description  
                   - resolution/ticket_resolution: Resolution details
                   
        Returns:
            str: Formatted text in format "Subject: {subject}\\nIssue: {description}\\nResolution: {resolution}"
            
        Note:
            - Handles missing/null fields gracefully
            - Skips sections if field is None
            - Uses empty string if field is missing from dict
        """
        # Handle different possible field names (with/without ticket_ prefix)
        subject = self._get_field_value(ticket, ['subject', 'ticket_subject'])
        description = self._get_field_value(ticket, ['description', 'ticket_description'])  
        resolution = self._get_field_value(ticket, ['resolution', 'ticket_resolution'])
        
        # Build formatted text, skipping None fields
        text_parts = []
        
        if subject is not None:
            text_parts.append(f"Subject: {subject}")
            
        if description is not None:
            text_parts.append(f"Issue: {description}")
            
        if resolution is not None:
            text_parts.append(f"Resolution: {resolution}")
        
        # Join with newlines, return empty string if no valid parts
        return "\n".join(text_parts) if text_parts else ""

    def _get_field_value(self, ticket: Dict[str, Any], field_names: List[str]) -> Optional[str]:
        """Get field value from ticket dict, trying multiple possible field names.
        
        Args:
            ticket: Ticket dictionary
            field_names: List of possible field names to try
            
        Returns:
            Optional[str]: Field value or None if not found/null
        """
        for field_name in field_names:
            if field_name in ticket:
                value = ticket[field_name]
                # Return None for None values, empty string for empty strings
                if value is None:
                    return None
                # Convert to string and strip whitespace
                str_value = str(value).strip()
                # Return None for empty strings after stripping
                return str_value if str_value else None
        
        # Field not found in ticket dict - return None to skip this section
        return None

    async def generate_ticket_embedding(self, ticket: Dict[str, Any]) -> List[float]:
        """Generate embedding for a ticket by combining its text fields.
        
        Args:
            ticket: Dictionary containing ticket information
            
        Returns:
            List[float]: 768-dimensional embedding vector
            
        Raises:
            Exception: If embedding generation fails or no valid text found
        """
        ticket_text = self.prepare_ticket_text(ticket)
        
        if not ticket_text:
            raise ValueError("No valid text found in ticket to generate embedding")
            
        return await self.generate_embedding(ticket_text)

    async def test_connection(self) -> Dict[str, str]:
        """Test the BigQuery connection and embedding model availability.
        
        Returns:
            Dict[str, str]: Status of the connection and model test
        """
        try:
            # Test basic BigQuery connection using BigQueryService
            bigquery_status = await self.bigquery_service.test_connection()
            
            if bigquery_status["status"] != "success":
                return {
                    "status": "error",
                    "message": f"BigQuery connection failed: {bigquery_status['message']}"
                }
            
            # Test embedding model with simple text
            test_embedding = await self.generate_embedding("Test connection")
            
            return {
                "status": "success",
                "message": f"BigQuery connection successful. Generated {len(test_embedding)}-dimensional embedding.",
                "embedding_dimension": len(test_embedding)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection or embedding test failed: {str(e)}"
            }


# Create a default instance
embedding_service = EmbeddingService()
