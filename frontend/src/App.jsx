import { useEffect, useState } from "react"
import { getHealth } from "./services/api"

function App() {
  const [message, setMessage] = useState("Loading...")
  
  const fetchData = async () => {
    try {
      setMessage("Loading...")
      const data = await getHealth()
      setMessage(data.message || JSON.stringify(data))
    } catch (error) {
      setMessage(`Error: ${error.message}`)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 dark:bg-background space-y-4">
      <h1 className="text-4xl font-bold text-gray-900 dark:text-primary">
        Hello, World!
      </h1>
      <p className="text-2xl font-medium text-gray-700 dark:text-primary">
        Network Health: {message}
      </p>
      <button
        onClick={fetchData}
        className="px-4 py-2 rounded-lg bg-secondary text-white font-semibold shadow hover:opacity-90 transition"
      >
        Reload
      </button>
    </div>
  )
}

export default App
