'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

const PLANS = {
  starter: { name: 'Starter', price: 9.99 },
  pro: { name: 'Pro', price: 24.99 },
  team: { name: 'Team', price: 49.99 },
}

export default function SubscribePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [plan, setPlan] = useState<string>('starter')
  const [error, setError] = useState('')

  useEffect(() => {
    const planParam = searchParams.get('plan')
    if (planParam && PLANS[planParam as keyof typeof PLANS]) {
      setPlan(planParam)
    }
  }, [searchParams])

  const handleSubscribe = async () => {
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      const response = await fetch('http://localhost:8000/api/payments/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ plan }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to create checkout')
      }

      const data = await response.json()

      // Redirect to LemonSqueezy checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.')
      setLoading(false)
    }
  }

  const selectedPlan = PLANS[plan as keyof typeof PLANS]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              PropertyPulse
            </Link>
            <Link href="/pricing" className="text-gray-600 hover:text-gray-900">
              Back to Pricing
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 py-16">
        <h1 className="text-3xl font-bold text-center mb-8">Complete Your Subscription</h1>

        {/* Plan Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Select Plan</h2>
          <div className="space-y-3">
            {Object.entries(PLANS).map(([key, value]) => (
              <label
                key={key}
                className={`flex items-center justify-between p-4 border rounded-lg cursor-pointer ${
                  plan === key ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                }`}
              >
                <div className="flex items-center">
                  <input
                    type="radio"
                    name="plan"
                    value={key}
                    checked={plan === key}
                    onChange={(e) => setPlan(e.target.value)}
                    className="mr-3"
                  />
                  <span className="font-medium">{value.name}</span>
                </div>
                <span className="text-lg font-bold">${value.price}/mo</span>
              </label>
            ))}
          </div>
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Order Summary</h2>
          <div className="flex justify-between mb-2">
            <span className="text-gray-600">{selectedPlan?.name} Plan</span>
            <span>${selectedPlan?.price}/month</span>
          </div>
          <div className="border-t pt-2 mt-2">
            <div className="flex justify-between font-bold">
              <span>Total</span>
              <span>${selectedPlan?.price}/month</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Subscribe Button */}
        <button
          onClick={handleSubscribe}
          disabled={loading}
          className="w-full bg-primary-600 text-white py-3 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 font-medium"
        >
          {loading ? 'Processing...' : `Subscribe to ${selectedPlan?.name}`}
        </button>

        <p className="text-center text-sm text-gray-500 mt-4">
          Secure payment powered by LemonSqueezy
        </p>
      </div>
    </div>
  )
}
