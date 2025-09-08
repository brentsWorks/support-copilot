const BASE_URL = "http://localhost:8000"

// GET /health
export async function getHealth() {
  try {
    const response = await fetch(`${BASE_URL}/health`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error("Error fetching health:", error)
    throw error
  }
}

// GET /tickets?limit=100
export async function getTickets(limit = 100) {
  try {
    const response = await fetch(`${BASE_URL}/tickets?limit=${limit}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error("Error fetching tickets:", error)
    throw error
  }
}

// GET /tickets/{ticket_id}
export async function getTicketById(ticketId) {
  try {
    const response = await fetch(`${BASE_URL}/tickets/${ticketId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error(`Error fetching ticket ${ticketId}:`, error)
    throw error
  }
}
