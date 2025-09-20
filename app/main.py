from fastapi import FastAPI, HTTPException
from app.services.bigquery_service import bigquery_service
from app.services.embedding_service import embedding_service
from app.services.retrieval_service import retrieval_service
from fastapi.middleware.cors import CORSMiddleware
from app.models.embeddings import EmbeddingRequest, EmbeddingResponse, EmbeddingTicketRequest, SimilarSearchRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Default react port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify BigQuery connection."""	
    try:
        connection_status = await bigquery_service.test_connection()
        if connection_status["status"] != "success":
            return {
                "status": "unhealthy",
                "message": connection_status["message"]
            }
        return {
            "status": "healthy",
            "message": "BigQuery connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"BigQuery connection failed: {str(e)}"
		}

@app.get('/tickets')
async def get_tickets(limit: int = 100):
    """Get tickets with their details."""
    tickets = await bigquery_service.get_tickets(limit)
    if tickets is None:
        raise HTTPException(
            status_code=404, 
            detail=f"No tickets found"
        )
    return tickets

@app.get('/tickets/{ticket_id}')
async def get_ticket_by_id(ticket_id: int):
    """Get a specific ticket by its ID."""
    ticket = await bigquery_service.get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Ticket with ID {ticket_id} not found"
        )
    return ticket

@app.post("/embedding", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """Generate embedding for plain text using the embedding service."""
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty or None"
            )
        
        embedding = await embedding_service.generate_embedding(request.text)
        
        return EmbeddingResponse(
            embedding=embedding,
            dimension=len(embedding),
            text=request.text
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embedding: {str(e)}"
        )

@app.post("/embedding/store/{ticket_id}")
async def store_ticket_embedding(ticket_id: int, request: EmbeddingTicketRequest):
    """
    Store an embedding for a given ticket.
    """
    try:
        result = await embedding_service.store_embedding(
            ticket_id=ticket_id,
            vector=request.vector,
            ticket_resolution=request.ticket_resolution,
            upsert=True  # allow update if already exists
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store embedding: {str(e)}")

@app.post("/search/similar")
async def search_similar(req: SimilarSearchRequest):
  """
  Semantic similarity search over tickets.
  Returns [] on no matches (no 404), consistent with other endpoints' graceful behavior.
  """
  try:
    results = await retrieval_service.search_similar_tickets(req.query, req.limit)
    return results
  except Exception as e:
    # retrieval_service already fails gracefully, but keep parity with existing style
    raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
