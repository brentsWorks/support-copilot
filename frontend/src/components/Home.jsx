import { testConnection } from "../services/api"
import { useEffect, useState } from "react"

export default function Home() {
	const [message, setMessage] = useState("Loading...")

	const fetchData = async () => {
		try {
			setMessage("Loading...")
			const data = await testConnection()
			setMessage(data.message || JSON.stringify(data))
		} catch (error) {
			setMessage(`Error: ${error.message}`)
		}
	}

	useEffect(() => {
		fetchData()
	}, [])

	return (
		<div>
			<h1>Home</h1>
			<p>Network Health: {message}</p>
			<button onClick={fetchData}>Reload</button>
		</div>
	)
}