import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import AuthPage from './pages/Auth'
import AgentIframe from './pages/AgentIframe'

export default function App(){
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/auth" element={<AuthPage/>} />
          <Route path="/agent/:agentId" element={<AgentRoute/>} />
          <Route path="/agents" element={<AgentsList/>} />
        </Routes>
      </div>
    </AuthProvider>
  )
}

function AgentRoute(){
  const agentId = window.location.pathname.split('/').pop()
  return <AgentIframe agentId={agentId} />
}

function AgentsList(){
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-semibold">Agents</h2>
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <a href="https://naman-jain-copywriting-agent.streamlit.app/?embed=true" className="p-4 bg-white rounded shadow">WriteAiDaily</a>
        <div className="p-4 bg-white rounded shadow">Agent 2 (coming soon)</div>
        <div className="p-4 bg-white rounded shadow">Agent 3 (coming soon)</div>
      </div>
    </div>
  )
}