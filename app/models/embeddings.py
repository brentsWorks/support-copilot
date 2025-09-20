from pydantic import BaseModel, Field
from typing import List

# Pydantic models for embedding request/response
class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int
    text: str

# Request body schema for storing an embedding
class EmbeddingTicketRequest(BaseModel):
    vector: List[float]
    ticket_resolution: str

class SimilarSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=50)
