from pydantic import BaseModel
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
    ticket_id: int
    vector: List[float]
    text: str