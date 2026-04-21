'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import api, { authApi } from '@/lib/api'

interface User {
  id: number
  email: string
  name: string
  subscription_plan: string
  searches_used: number
  searches_limit: number
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // 检查本地存储的token
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')

    if (token && userStr) {
      setUser(JSON.parse(userStr))
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password)
    localStorage.setItem('token', response.access_token)

    const userInfo = await authApi.getMe()
    localStorage.setItem('user', JSON.stringify(userInfo))
    setUser(userInfo)
  }

  const register = async (email: string, password: string, name: string) => {
    await authApi.register(email, password, name)
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    router.push('/')
  }

  const refreshUser = async () => {
    try {
      const userInfo = await authApi.getMe()
      localStorage.setItem('user', JSON.stringify(userInfo))
      setUser(userInfo)
    } catch (error) {
      logout()
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
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
