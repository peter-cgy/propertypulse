'use client'

import { useState } from 'react'

interface PropertyData {
  id?: number
  address: string
  city: string
  state: string
  property_type: string
  bedrooms: number
  bathrooms: number
  square_feet: number
  year_built?: number
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

interface MarketInsight {
  type: string
  title: string
  description: string
}

interface MarketInsights {
  grade: string
  insights: MarketInsight[]
  recommendation: string
}

interface PropertyCardProps {
  property: PropertyData
  analysis: AnalysisData
  marketInsights: MarketInsights
}

export default function PropertyCard({ property, analysis, marketInsights }: PropertyCardProps) {
  const [generatingPdf, setGeneratingPdf] = useState(false)

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price)
  }

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'bg-green-500 text-white'
      case 'B': return 'bg-blue-500 text-white'
      case 'C': return 'bg-yellow-500 text-white'
      case 'D': return 'bg-red-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'positive': return '[+]'
      case 'warning': return '[!]'
      case 'neutral': return '[i]'
      default: return '[i]'
    }
  }

  const getInsightBg = (type: string) => {
    switch (type) {
      case 'positive': return 'bg-green-50 border-green-200'
      case 'warning': return 'bg-red-50 border-red-200'
      case 'neutral': return 'bg-blue-50 border-blue-200'
      default: return 'bg-gray-50 border-gray-200'
    }
  }

  const handleDownloadPdf = async () => {
    setGeneratingPdf(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          property_data: property,
          analysis_data: analysis,
          market_insights: marketInsights,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        alert(error.detail || 'Failed to generate report')
        return
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `PropertyPulse_Report.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      a.remove()
    } catch (error) {
      alert('Failed to generate PDF. Please try again.')
    } finally {
      setGeneratingPdf(false)
    }
  }

  return (
    <div className="border rounded-xl overflow-hidden shadow-lg">
      {/* Property Image Placeholder */}
      <div className="bg-gradient-to-r from-blue-400 to-blue-600 h-48 flex items-center justify-center relative">
        <span className="text-white text-6xl">🏠</span>
        {/* Investment Grade Badge */}
        <div className={`absolute top-4 right-4 px-4 py-2 rounded-lg text-xl font-bold ${getGradeColor(analysis.investment_grade)}`}>
          Grade {analysis.investment_grade}
        </div>
      </div>

      <div className="p-6">
        {/* Address */}
        <h3 className="text-xl font-bold text-gray-900 mb-2">{property.address}</h3>
        <p className="text-gray-500 mb-4">{property.city}, {property.state}</p>

        {/* Basic Info */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="bg-gray-50 p-3 rounded-lg text-center">
            <p className="text-xs text-gray-500">Type</p>
            <p className="font-semibold text-sm">{property.property_type}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg text-center">
            <p className="text-xs text-gray-500">Beds/Baths</p>
            <p className="font-semibold text-sm">{property.bedrooms} / {property.bathrooms}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg text-center">
            <p className="text-xs text-gray-500">Sq Ft</p>
            <p className="font-semibold text-sm">{property.square_feet?.toLocaleString()}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg text-center">
            <p className="text-xs text-gray-500">Year Built</p>
            <p className="font-semibold text-sm">{property.year_built || 'N/A'}</p>
          </div>
        </div>

        {/* Price Info */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-600">Price Estimate</p>
            <p className="text-2xl font-bold text-blue-700">{formatPrice(property.price_estimate)}</p>
            <p className="text-xs text-blue-500 mt-1">${analysis.price_per_sqft}/sqft</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-green-600">Rent Estimate</p>
            <p className="text-2xl font-bold text-green-700">{formatPrice(property.rent_estimate)}/mo</p>
            <p className="text-xs text-green-500 mt-1">${analysis.rent_per_sqft}/sqft</p>
          </div>
        </div>

        {/* Investment Analysis */}
        <div className="border-t pt-4 mb-4">
          <h4 className="font-semibold mb-3">Investment Analysis</h4>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-2 bg-gray-50 rounded">
              <p className="text-xs text-gray-500">CAP Rate</p>
              <p className={`text-lg font-bold ${analysis.cap_rate >= 6 ? 'text-green-600' : analysis.cap_rate >= 4 ? 'text-blue-600' : 'text-orange-500'}`}>
                {analysis.cap_rate}%
              </p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <p className="text-xs text-gray-500">Monthly CF</p>
              <p className={`text-lg font-bold ${analysis.monthly_cashflow > 0 ? 'text-green-600' : 'text-red-500'}`}>
                {formatPrice(analysis.monthly_cashflow)}
              </p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <p className="text-xs text-gray-500">Cash-on-Cash</p>
              <p className={`text-lg font-bold ${analysis.cash_on_cash_return > 8 ? 'text-green-600' : analysis.cash_on_cash_return > 0 ? 'text-blue-600' : 'text-red-500'}`}>
                {analysis.cash_on_cash_return}%
              </p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <p className="text-xs text-gray-500">GRM</p>
              <p className="text-lg font-bold text-gray-700">
                {analysis.gross_rent_multiplier}yr
              </p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <p className="text-xs text-gray-500">Annual CF</p>
              <p className={`text-lg font-bold ${analysis.annual_cashflow > 0 ? 'text-green-600' : 'text-red-500'}`}>
                {formatPrice(analysis.annual_cashflow)}
              </p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <p className="text-xs text-gray-500">Break-Even</p>
              <p className={`text-lg font-bold ${analysis.break_even_ratio <= 70 ? 'text-green-600' : analysis.break_even_ratio <= 85 ? 'text-blue-600' : 'text-orange-500'}`}>
                {analysis.break_even_ratio}%
              </p>
            </div>
          </div>
        </div>

        {/* Market Insights */}
        <div className="border-t pt-4 mb-4">
          <h4 className="font-semibold mb-3">Market Insights</h4>
          <div className="space-y-2">
            {marketInsights.insights.map((insight, idx) => (
              <div key={idx} className={`p-3 rounded-lg border ${getInsightBg(insight.type)}`}>
                <div className="flex items-start">
                  <span className="mr-2 font-mono text-sm">{getInsightIcon(insight.type)}</span>
                  <div>
                    <p className="font-medium text-sm">{insight.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{insight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendation */}
        <div className={`p-4 rounded-lg ${marketInsights.recommendation === 'Recommended' ? 'bg-green-100 border border-green-300' : 'bg-yellow-100 border border-yellow-300'}`}>
          <p className="font-semibold text-center">
            {marketInsights.recommendation}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex gap-3">
          <button
            onClick={handleDownloadPdf}
            disabled={generatingPdf}
            className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 font-medium disabled:bg-gray-400"
          >
            {generatingPdf ? 'Generating...' : 'Download PDF Report'}
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Save
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Share
          </button>
        </div>
      </div>
    </div>
  )
}
