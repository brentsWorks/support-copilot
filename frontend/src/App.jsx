import Layout from './components/Layout'
import Home from './components/Home'
import CustomerDashboard from './pages/CustomerDashboard'
import AgentDashboard from './pages/AgentDashboard'

import { BrowserRouter, Routes, Route } from 'react-router-dom'
function App() {

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/customer" element={ <CustomerDashboard /> } />
          <Route path="/agent" element={<AgentDashboard /> } />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
