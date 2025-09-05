from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

class Ticket(BaseModel):
    ticket_id: int
    ticket_subject: str
    ticket_description: str
    ticket_resolution: Optional[str] = Field(None, min_length=1,description="Ticket resolution (if present) cannot be empty")
    ticket_status: str
    ticket_created_at: date

class SimilarTicket(BaseModel):
	ticket_id: int
	ticket_subject: str
	ticket_description: str
	ticket_resolution: Optional[str] = Field(None, min_length=1,description="Ticket resolution (if present) cannot be empty")	
	ticket_status: str
	ticket_created_at: date
	similarity_score: float = Field(ge=0.0, le=1.0,description="Similarity score between 0.0 and 1.0")

class SearchRequest(BaseModel):
    query: str = Field(min_length=3, description="Search query (minimum 3 characters)")
    limit: int = Field(default=5, le=20, description="Maximum number of results (default: 5, maximum: 20)")
    min_similarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold for matching tickets (0.0 to 1.0)"
	)

class SearchResponse(BaseModel):
    query: str = Field(description="Search response query")
    results: List[SimilarTicket] = Field(description="List of matched similar tickets")
    total_found: int = Field(description="Total number of similar tickets found")
