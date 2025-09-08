import Layout from './components/Layout'
import Home from './components/Home'

import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/customer" element={<h1>Customer View</h1>} />
          <Route path="/agent" element={<h1>Agent View</h1>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
