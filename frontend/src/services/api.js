export async function getHealth() {
  try {
    const response = await fetch("http://localhost:8000/health");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching health:", error);
    throw error;
  }
}
