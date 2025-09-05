from datetime import date
import pytest
from app.models.ticket import Ticket, SimilarTicket, SearchRequest, SearchResponse

def test_ticket_model():
    """Test Ticket model serialization and deserialization."""
    # Test with no resolution (unresolved ticket)
    ticket_data = {
        "ticket_id": 1,
        "ticket_subject": "Login issue",
        "ticket_description": "User cannot login to the application",
        "ticket_resolution": None,
        "ticket_status": "open",
        "ticket_created_at": "2024-03-14"
    }
    ticket = Ticket(**ticket_data)
    assert ticket.ticket_id == 1
    assert ticket.ticket_resolution is None
    
    # Test with resolution (resolved ticket)
    resolved_ticket_data = ticket_data.copy()
    resolved_ticket_data["ticket_resolution"] = "Password reset completed"
    resolved_ticket = Ticket(**resolved_ticket_data)
    assert resolved_ticket.ticket_resolution == "Password reset completed"

def test_similar_ticket_model():
    """Test SimilarTicket model with similarity score."""
    similar_ticket_data = {
        "ticket_id": 2,
        "ticket_subject": "Cannot login",
        "ticket_description": "Authentication failing for user",
        "ticket_resolution": "Reset user password",
        "ticket_status": "resolved",
        "ticket_created_at": date(2024, 3, 14),
        "similarity_score": 0.95
    }
    similar_ticket = SimilarTicket(**similar_ticket_data)
    assert similar_ticket.similarity_score == 0.95
    assert similar_ticket.ticket_status == "resolved"

def test_search_request_model():
    """Test SearchRequest model validation."""
    # Test valid request
    valid_request = SearchRequest(
        query="login issues",
        limit=10,
        min_similarity=0.7
    )
    assert valid_request.limit == 10
    assert valid_request.min_similarity == 0.7

    # Test default values
    minimal_request = SearchRequest(query="test")
    assert minimal_request.limit == 5  # default value
    assert minimal_request.min_similarity == 0.0  # default value

def test_search_response_model():
    """Test SearchResponse model with results."""
    similar_ticket = SimilarTicket(
        ticket_id=1,
        ticket_subject="Login issue",
        ticket_description="Cannot access account",
        ticket_resolution=None,
        ticket_status="open",
        ticket_created_at=date(2024, 3, 14),
        similarity_score=0.9
    )
    
    response = SearchResponse(
        query="login",
        results=[similar_ticket],
        total_found=1
    )
    assert len(response.results) == 1
    assert response.total_found == 1
    assert response.results[0].similarity_score == 0.9

def test_validation_errors():
    """Test model validation errors."""
    with pytest.raises(ValueError):
        # Test query too short
        SearchRequest(query="ab")
    
    with pytest.raises(ValueError):
        # Test limit too high
        SearchRequest(query="test", limit=21)
    
    with pytest.raises(ValueError):
        # Test similarity score out of range
        SearchRequest(query="test", min_similarity=1.1)
    
    with pytest.raises(ValueError):
        # Test empty resolution string
        SimilarTicket(
            ticket_id=1,
            ticket_subject="Test",
            ticket_description="Test description",
            ticket_resolution="",  # Should not allow empty string
            ticket_status="open",
            ticket_created_at=date(2024, 3, 14),
            similarity_score=0.9
        )
