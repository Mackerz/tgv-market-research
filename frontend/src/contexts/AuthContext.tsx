'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { logger } from '@/lib/logger'
import { authService, type User as AuthUser } from '@/lib/api/services/auth'

interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  is_active: boolean
  is_admin: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  loginWithGoogle: (credential: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const checkAuth = async () => {
    try {
      const userData = await authService.getMe()
      setUser(userData)
    } catch (error) {
      logger.error('Auth check failed:', error)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    const data = await authService.login(username, password)
    setUser(data)
  }

  const loginWithGoogle = async (credential: string) => {
    const data = await authService.googleLogin(credential)
    setUser(data)
  }

  const logout = async () => {
    await authService.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, loginWithGoogle, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
