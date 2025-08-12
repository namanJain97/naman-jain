import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function AgentIframe({ agentId }) {
  const { user } = useAuth()
  const [idToken, setIdToken] = useState(null)

  useEffect(() => {
    let mounted = true
    async function fetchToken() {
      if (!user) return
      const token = await user.getIdToken()
      if (mounted) setIdToken(token)
    }
    fetchToken()
    return () => { mounted = false }
  }, [user])

  const agentMap = {
    writeaidaily: import.meta.env.VITE_WRITEAIDAILY_URL || 'https://your-writeaidaily.hf.space'
  }
  const src = agentMap[agentId] + (idToken ? `?id_token=${encodeURIComponent(idToken)}` : '')

  if (!user) {
    return <div className="p-6">Please login to access this agent.</div>
  }

  return (
    <div className="h-[80vh] p-4">
      <iframe title={agentId} src={src} className="w-full h-full border rounded" />
    </div>
  )
}
