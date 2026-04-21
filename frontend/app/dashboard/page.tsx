'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { propertyApi } from '@/lib/api'
import PropertyCard from '@/components/PropertyCard'

interface UserInfo {
  id: number
  email: string
  name: string
  subscription_plan: string
  searches_used: number
  searches_limit: number
}

interface PropertyData {
  address: string
  city: string
  state: string
  property_type: string
  bedrooms: number
  bathrooms: number
  square_feet: number
  year_built: number
  price_estimate: number
  rent_estimate: number
}

interface AnalysisData {
  cap_rate: number
  gross_rent_multiplier: number
  monthly_cashflow: number
  annual_cashflow: number
  cash_on_cash_return: number
  price_per_sqft: number
  rent_per_sqft: number
  break_even_ratio: number
  investment_grade: string
}

interface MarketInsights {
  grade: string
  insights: Array<{
    type: string
    title: string
    description: string
  }>
  recommendation: string
}

interface SearchResult {
  property: PropertyData
  analysis: AnalysisData
  market_insights: MarketInsights
}

interface SavedSearch {
  address: string
  grade: string
  cap_rate: number
  timestamp: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<UserInfo | null>(null)
  const [searchAddress, setSearchAddress] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null)
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')

    if (!token || !userStr) {
      router.push('/login')
      return
    }

    setUser(JSON.parse(userStr))
  }, [router])

  const handleSearch = async () => {
    if (!searchAddress.trim()) return

    setSearching(true)
    setError('')
    try {
      const result = await propertyApi.search(searchAddress)
      setSearchResult(result)

      const newSearch: SavedSearch = {
        address: searchAddress,
        grade: result.analysis.investment_grade,
        cap_rate: result.analysis.cap_rate,
        timestamp: new Date().toLocaleString()
      }
      setSavedSearches([newSearch, ...savedSearches.slice(0, 9)])
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (detail?.includes('limit')) {
        setError('Monthly search limit reached. Please upgrade your plan.')
      } else {
        setError('Search failed. Please try again.')
      }
    } finally {
      setSearching(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  const getPlanName = (plan: string) => {
    const names: Record<string, string> = {
      free: 'Free',
      starter: 'Starter',
      pro: 'Pro',
      team: 'Team',
    }
    return names[plan] || plan
  }

  const getPlanColor = (plan: string) => {
    const colors: Record<string, string> = {
      free: 'bg-gray-100 text-gray-800',
      starter: 'bg-blue-100 text-blue-800',
      pro: 'bg-purple-100 text-purple-800',
      team: 'bg-yellow-100 text-yellow-800',
    }
    return colors[plan] || 'bg-gray-100 text-gray-800'
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  const usagePercent = (user.searches_used / user.searches_limit) * 100

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              PropertyPulse
            </Link>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">{user.email}</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getPlanColor(user.subscription_plan)}`}>
                {getPlanName(user.subscription_plan)}
              </span>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Search Property</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={searchAddress}
              onChange={(e) => setSearchAddress(e.target.value)}
              placeholder="Enter US property address, e.g., 123 Main St, New York, NY"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={searching || !searchAddress.trim()}
              className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 font-medium"
            >
              {searching ? 'Searching...' : 'Analyze'}
            </button>
          </div>

          {/* Usage indicator */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex-1 bg-gray-200 rounded-full h-2 w-32">
                <div
                  className={`h-2 rounded-full ${usagePercent >= 100 ? 'bg-red-500' : usagePercent >= 80 ? 'bg-yellow-500' : 'bg-primary-600'}`}
                  style={{ width: `${Math.min(usagePercent, 100)}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-500">
                {user.searches_used} / {user.searches_limit} searches this month
              </span>
            </div>
            {user.searches_used >= user.searches_limit && (
              <Link href="/pricing" className="text-primary-600 hover:underline text-sm">
                Upgrade Plan
              </Link>
            )}
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Search Result */}
        {searchResult && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4">Analysis Result</h2>
            <PropertyCard
              property={searchResult.property}
              analysis={searchResult.analysis}
              marketInsights={searchResult.market_insights}
            />
          </div>
        )}

        {/* Recent Searches */}
        {savedSearches.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Searches</h2>
            <div className="space-y-2">
              {savedSearches.map((search, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  onClick={() => setSearchAddress(search.address)}
                >
                  <div>
                    <p className="font-medium">{search.address}</p>
                    <p className="text-sm text-gray-500">{search.timestamp}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">CAP: {search.cap_rate}%</span>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      search.grade === 'A' ? 'bg-green-100 text-green-800' :
                      search.grade === 'B' ? 'bg-blue-100 text-blue-800' :
                      search.grade === 'C' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      Grade {search.grade}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
