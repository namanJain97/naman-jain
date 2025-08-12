import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-800">WriteAiPortal</Link>
            <nav className="ml-6 space-x-4 hidden md:flex">
              <Link to="/" className="text-gray-600 hover:text-gray-900">Home</Link>
              <Link to="/agents" className="text-gray-600 hover:text-gray-900">Agents</Link>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <button
                  onClick={() => navigate('/agent/writeaidaily')}
                  className="px-4 py-2 rounded-md bg-green-500 text-white font-semibold"
                >
                  Open WriteAiDaily
                </button>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-700">{user.displayName || user.email}</span>
                  <button
                    onClick={async () => { await signOut() }}
                    className="px-3 py-1 border rounded-md"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link to="/auth" className="px-4 py-2 rounded-md border">Login / Register</Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
