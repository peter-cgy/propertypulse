import Link from 'next/link'
import SearchForm from '@/components/SearchForm'

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">PropertyPulse</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/pricing" className="text-gray-600 hover:text-gray-900">
                Pricing
              </Link>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                Start Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-primary-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Get Professional Real Estate
            <br />
            <span className="text-primary-600">Investment Analysis in 5 Minutes</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Enter any US property address to get price estimates, rent analysis, school ratings,
            and crime data - all in one comprehensive report.
          </p>

          {/* Search Form */}
          <SearchForm />
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Why PropertyPulse?</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <FeatureCard
              icon="🏠"
              title="All-in-One Data"
              description="Property data from multiple sources in one place"
            />
            <FeatureCard
              icon="📊"
              title="Investment Analysis"
              description="CAP Rate, cash flow, ROI calculations instantly"
            />
            <FeatureCard
              icon="🗺️"
              title="Location Intelligence"
              description="Commute analysis, amenities, risk assessment"
            />
            <FeatureCard
              icon="📄"
              title="PDF Reports"
              description="Download and share professional analysis reports"
            />
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Simple, Transparent Pricing</h2>
          <p className="text-gray-600 mb-8">Start free, upgrade anytime</p>
          <Link
            href="/pricing"
            className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 inline-block"
          >
            View Pricing Plans
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="text-2xl font-bold">PropertyPulse</span>
            <p className="mt-4 text-gray-400">
              © 2026 PropertyPulse. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
