import { Link, useLocation } from 'react-router-dom'

export default function Layout({children}) {
  const location = useLocation();
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
				<Link to="/">
					Support Copilot
				</Link>
              </h1>
            </div>
            <nav className="flex space-x-8">
              <Link
                to="/customer"
                className={`${
                  location.pathname === '/customer' 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                } px-3 py-2 text-sm font-medium transition-colors duration-200`}
              >
                Customer View
              </Link>
              <Link
                to="/agent"
                className={`${
                  location.pathname === '/agent' 
                    ? 'text-blue-600 border-b-2 border-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                } px-3 py-2 text-sm font-medium transition-colors duration-200`}
              >
                Agent Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  )
}