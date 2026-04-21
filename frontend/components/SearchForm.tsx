'use client'

import { useState } from 'react'

export default function SearchForm() {
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!address.trim()) return

    setLoading(true)
    // TODO: Call backend API
    console.log('Searching for:', address)

    // Simulate search
    setTimeout(() => {
      setLoading(false)
      alert(`Search feature coming soon...\nAddress: ${address}`)
    }, 1000)
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
      <div className="flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Enter US property address, e.g., 123 Main St, New York, NY"
          className="flex-1 px-6 py-4 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-primary-600 text-white px-8 py-4 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 text-lg font-medium"
        >
          {loading ? 'Searching...' : 'Analyze'}
        </button>
      </div>
      <p className="text-sm text-gray-500 mt-3">
        Free users get 3 searches per month
      </p>
    </form>
  )
}
