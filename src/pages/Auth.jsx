import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import zxcvbn from 'zxcvbn'

export default function AuthPage() {
  const { signup, login, googleSignIn, forgotPassword, isUsernameUnique } = useAuth()
  const [isSignup, setIsSignup] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', username: '', fullName: '' })
  const [passwordScore, setPasswordScore] = useState(null)
  const [usernameAvailable, setUsernameAvailable] = useState(null)
  const [message, setMessage] = useState(null)

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
    if (e.target.name === 'password') {
      setPasswordScore(zxcvbn(e.target.value).score)
    }
  }

  async function checkUsername() {
    if (!form.username) return
    const ok = await isUsernameUnique(form.username)
    setUsernameAvailable(ok)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setMessage(null)
    try {
      if (isSignup) {
        if (passwordScore < 2) { setMessage('Password too weak — please choose a stronger password.') ; return }
        const ok = await isUsernameUnique(form.username)
        if (!ok) { setMessage('Username already taken. Choose another.') ; return }
        await signup(form)
        setMessage('Signup successful — verification email sent. Please verify your email before first use.')
      } else {
        await login(form)
        setMessage('Login successful')
      }
    } catch (err) {
      setMessage('Error: ' + err.message)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-12 bg-white p-6 rounded-xl shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{isSignup ? 'Create an account' : 'Log in'}</h2>
        <button className="text-sm text-blue-600" onClick={() => setIsSignup(!isSignup)}>
          {isSignup ? 'Already have an account?' : "Don't have an account?"}
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {isSignup && (
          <>
            <input name="fullName" placeholder="Full name" value={form.fullName} onChange={handleChange} className="w-full p-2 border rounded" />
            <div className="flex gap-2">
              <input name="username" placeholder="Username" value={form.username} onChange={handleChange} className="w-full p-2 border rounded" />
              <button type="button" onClick={checkUsername} className="px-3 py-2 border rounded">Check</button>
            </div>
            {usernameAvailable === true && <p className="text-green-600 text-sm">Username is available</p>}
            {usernameAvailable === false && <p className="text-red-600 text-sm">Username taken</p>}
          </>
        )}

        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} className="w-full p-2 border rounded" />
        {form.password && (
          <div className="text-sm">
            <PasswordStrength score={passwordScore} />
          </div>
        )}

        <div className="flex gap-2">
          <button type="submit" className="flex-1 px-4 py-2 bg-green-500 text-white rounded">{isSignup ? 'Sign up' : 'Log in'}</button>
          <button type="button" className="flex-1 px-4 py-2 border rounded" onClick={() => googleSignIn()}>Continue with Google</button>
        </div>

        {!isSignup && (
          <div className="text-right">
            <button type="button" className="text-sm text-blue-600" onClick={() => { const email = form.email; if (email) forgotPassword(email).then(()=>setMessage('Password reset email sent')).catch(e=>setMessage(e.message)) }}>Forgot password?</button>
          </div>
        )}

        {message && <div className="p-2 text-sm bg-gray-100 rounded">{message}</div>}
      </form>
    </div>
  )
}

function PasswordStrength({ score }) {
  const labels = ['Very weak','Weak','Fair','Good','Strong']
  return (
    <div className="flex items-center gap-3">
      <div className="w-full bg-gray-200 h-2 rounded overflow-hidden">
        <div style={{ width: `${((score||0)+1)*20}%` }} className={`h-2 ${score>=3? 'bg-green-500': score===2? 'bg-yellow-400': 'bg-red-500'}`}></div>
      </div>
      <div className="text-sm">{labels[score||0]}</div>
    </div>
  )
}
