"""
Tests for the EmbeddingService class.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test cases for EmbeddingService."""

    @pytest.fixture
    def mock_bigquery_client(self):
        """Mock BigQuery client for testing."""
        with patch('app.services.embedding_service.bigquery.Client') as mock_client:
            yield mock_client

    @pytest.fixture
    def embedding_service(self, mock_bigquery_client):
        """Create EmbeddingService instance with mocked dependencies."""
        with patch('app.services.embedding_service.service_account.Credentials.from_service_account_file'):
            service = EmbeddingService()
            service.client = Mock()
            return service

    @pytest.mark.asyncio
    async def test_generate_embedding_success(self, embedding_service):
        """Test successful embedding generation."""
        # Mock the query result with 768-dimensional embedding
        mock_embedding = [0.1] * 768  # 768-dimensional vector
        mock_row = Mock()
        mock_row.ml_generate_text_embedding_result = mock_embedding
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        embedding_service.client.query.return_value = mock_query_job
        
        # Test
        result = await embedding_service.generate_embedding("test text")
        
        # Assertions
        assert result == mock_embedding
        assert len(result) == 768
        embedding_service.client.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self, embedding_service):
        """Test embedding generation with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty or None"):
            await embedding_service.generate_embedding("")
        
        with pytest.raises(ValueError, match="Text cannot be empty or None"):
            await embedding_service.generate_embedding("   ")

    @pytest.mark.asyncio
    async def test_generate_embedding_failure(self, embedding_service):
        """Test embedding generation failure."""
        # Mock query failure
        embedding_service.client.query.side_effect = Exception("Query failed")
        
        # Test and assert exception
        with pytest.raises(Exception, match="Failed to generate embedding"):
            await embedding_service.generate_embedding("test text")

    @pytest.mark.asyncio
    async def test_generate_embedding_wrong_dimensions(self, embedding_service):
        """Test embedding generation with wrong dimensions."""
        # Mock result with wrong dimensions
        mock_embedding = [0.1] * 512  # Wrong dimension
        mock_row = Mock()
        mock_row.ml_generate_text_embedding_result = mock_embedding
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        embedding_service.client.query.return_value = mock_query_job
        
        # Test and assert exception
        with pytest.raises(Exception, match="Expected 768-dimensional vector"):
            await embedding_service.generate_embedding("test text")

    def test_prepare_ticket_text_complete(self, embedding_service):
        """Test prepare_ticket_text with complete ticket."""
        ticket = {
            "ticket_subject": "Login Issues",
            "ticket_description": "User cannot log into their account",
            "ticket_resolution": "Reset password and cleared cache"
        }
        
        result = embedding_service.prepare_ticket_text(ticket)
        expected = "Subject: Login Issues\nIssue: User cannot log into their account\nResolution: Reset password and cleared cache"
        
        assert result == expected

    def test_prepare_ticket_text_partial(self, embedding_service):
        """Test prepare_ticket_text with partial ticket."""
        ticket = {
            "subject": "Password Reset",
            "description": "Need password reset"
            # resolution missing
        }
        
        result = embedding_service.prepare_ticket_text(ticket)
        expected = "Subject: Password Reset\nIssue: Need password reset"
        
        assert result == expected

    def test_prepare_ticket_text_with_nulls(self, embedding_service):
        """Test prepare_ticket_text with null/empty values."""
        ticket = {
            "ticket_subject": "Test Subject",
            "ticket_description": None,  # null value
            "ticket_resolution": ""      # empty string
        }
        
        result = embedding_service.prepare_ticket_text(ticket)
        expected = "Subject: Test Subject"
        
        assert result == expected

    def test_prepare_ticket_text_empty_ticket(self, embedding_service):
        """Test prepare_ticket_text with empty ticket."""
        ticket = {}
        
        result = embedding_service.prepare_ticket_text(ticket)
        
        assert result == ""

    def test_prepare_ticket_text_all_null(self, embedding_service):
        """Test prepare_ticket_text with all null values."""
        ticket = {
            "ticket_subject": None,
            "ticket_description": None,
            "ticket_resolution": None
        }
        
        result = embedding_service.prepare_ticket_text(ticket)
        
        assert result == ""

    def test_prepare_ticket_text_whitespace_handling(self, embedding_service):
        """Test prepare_ticket_text handles whitespace correctly."""
        ticket = {
            "subject": "  Test Subject  ",
            "description": "   ",  # only whitespace
            "resolution": "Fixed it"
        }
        
        result = embedding_service.prepare_ticket_text(ticket)
        expected = "Subject: Test Subject\nResolution: Fixed it"
        
        assert result == expected

    def test_get_field_value_multiple_names(self, embedding_service):
        """Test _get_field_value with multiple possible field names."""
        ticket = {
            "ticket_subject": "Test Subject"
        }
        
        # Should find ticket_subject when looking for subject or ticket_subject
        result = embedding_service._get_field_value(ticket, ['subject', 'ticket_subject'])
        
        assert result == "Test Subject"

    def test_get_field_value_not_found(self, embedding_service):
        """Test _get_field_value when field is not found."""
        ticket = {
            "other_field": "value"
        }
        
        result = embedding_service._get_field_value(ticket, ['subject', 'ticket_subject'])
        
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_ticket_embedding_success(self, embedding_service):
        """Test successful ticket embedding generation."""
        ticket = {
            "subject": "Test",
            "description": "Test issue"
        }
        
        # Mock the generate_embedding method
        mock_embedding = [0.1] * 768
        with patch.object(embedding_service, 'generate_embedding', return_value=mock_embedding):
            result = await embedding_service.generate_ticket_embedding(ticket)
            
            assert result == mock_embedding
            assert len(result) == 768

    @pytest.mark.asyncio
    async def test_generate_ticket_embedding_empty_ticket(self, embedding_service):
        """Test ticket embedding generation with empty ticket."""
        ticket = {}
        
        with pytest.raises(ValueError, match="No valid text found in ticket"):
            await embedding_service.generate_ticket_embedding(ticket)

    @pytest.mark.asyncio
    async def test_test_connection_success(self, embedding_service):
        """Test successful connection test."""
        # Mock list_datasets
        mock_datasets = [Mock(), Mock()]  # 2 datasets
        embedding_service.client.list_datasets.return_value = mock_datasets
        
        # Mock generate_embedding
        mock_embedding = [0.1] * 768
        with patch.object(embedding_service, 'generate_embedding', return_value=mock_embedding):
            result = await embedding_service.test_connection()
            
            assert result["status"] == "success"
            assert "2 datasets" in result["message"]
            assert result["embedding_dimension"] == 768

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, embedding_service):
        """Test connection test failure."""
        # Mock connection failure
        embedding_service.client.list_datasets.side_effect = Exception("Connection failed")
        
        result = await embedding_service.test_connection()
        
        assert result["status"] == "error"
        assert "Connection failed" in result["message"]

    def test_initialization(self):
        """Test EmbeddingService initialization."""
        with patch('app.services.embedding_service.bigquery.Client'), \
             patch('app.services.embedding_service.service_account.Credentials.from_service_account_file'), \
             patch('app.services.embedding_service.settings') as mock_settings:
            
            mock_settings.GOOGLE_CLOUD_PROJECT = "test-project"
            mock_settings.BIGQUERY_DATASET_ID = "test-dataset"
            
            service = EmbeddingService()
            
            assert service.project_id == "test-project"
            assert service.dataset_id == "test-dataset"
