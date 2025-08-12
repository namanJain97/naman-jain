import React, { createContext, useContext, useEffect, useState } from 'react'
import { auth, googleProvider, db } from '../firebase'
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  signInWithPopup,
  sendEmailVerification,
  sendPasswordResetEmail,
  onAuthStateChanged
} from 'firebase/auth'
import { doc, setDoc, getDoc, collection, query, where, getDocs } from 'firebase/firestore'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (u) => {
      setUser(u)
      setLoading(false)
    })
    return unsubscribe
  }, [])

  async function signup({ email, password, username, fullName }) {
    const res = await createUserWithEmailAndPassword(auth, email, password)
    const uid = res.user.uid
    await setDoc(doc(db, 'users', uid), {
      username: username.toLowerCase(),
      email,
      fullName,
      createdAt: new Date().toISOString()
    })
    await sendEmailVerification(res.user)
    return res
  }

  async function login({ email, password }) {
    return await signInWithEmailAndPassword(auth, email, password)
  }

  async function googleSignIn() {
    return await signInWithPopup(auth, googleProvider)
  }

  async function signOut() {
    await firebaseSignOut(auth)
    setUser(null)
  }

  async function forgotPassword(email) {
    return await sendPasswordResetEmail(auth, email)
  }

  async function isUsernameUnique(username) {
    const q = query(collection(db, 'users'), where('username', '==', username.toLowerCase()))
    const snap = await getDocs(q)
    return snap.empty
  }

  const value = {
    user,
    loading,
    signup,
    login,
    signOut,
    googleSignIn,
    forgotPassword,
    isUsernameUnique
  }

  return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>
}
