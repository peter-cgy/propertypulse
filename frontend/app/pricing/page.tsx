import Link from 'next/link'

export default function PricingPage() {
  const plans = [
    {
      name: 'Free',
      price: 0,
      searches: 3,
      features: [
        '3 searches per month',
        'Basic property data',
        'No PDF reports',
        'No investment analysis',
      ],
      popular: false,
      buttonText: 'Start Free',
    },
    {
      name: 'Starter',
      price: 9.99,
      searches: 30,
      features: [
        '30 searches per month',
        'Full property data',
        'PDF report downloads',
        'Investment analysis',
        'Email support',
      ],
      popular: true,
      buttonText: 'Get Started',
    },
    {
      name: 'Pro',
      price: 24.99,
      searches: 100,
      features: [
        '100 searches per month',
        'Full property data',
        'PDF report downloads',
        'Investment analysis',
        'Location intelligence',
        'Priority support',
      ],
      popular: false,
      buttonText: 'Get Started',
    },
    {
      name: 'Team',
      price: 49.99,
      searches: 999,
      features: [
        'Unlimited searches',
        'Full property data',
        'PDF report downloads',
        'Investment analysis',
        'Location intelligence',
        '5 team seats',
        'API access',
      ],
      popular: false,
      buttonText: 'Contact Us',
    },
  ]

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

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">Simple, Transparent Pricing</h1>
          <p className="mt-4 text-xl text-gray-500">
            Choose the plan that fits your needs. Cancel anytime.
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`bg-white rounded-xl shadow-sm border-2 ${
                plan.popular ? 'border-primary-500 relative' : 'border-gray-200'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary-500 text-white text-sm px-3 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900">{plan.name}</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-500">/month</span>
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  {plan.searches >= 999 ? 'Unlimited' : plan.searches} searches/month
                </p>

                <ul className="mt-6 space-y-3">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-sm text-gray-600">
                      <svg
                        className="w-4 h-4 text-green-500 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.price === 0 ? '/register' : '/subscribe?plan=' + plan.name.toLowerCase()}
                  className={`mt-6 block w-full text-center py-3 rounded-lg font-medium ${
                    plan.popular
                      ? 'bg-primary-600 text-white hover:bg-primary-700'
                      : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {plan.buttonText}
                </Link>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
            <FAQItem
              question="Can I cancel anytime?"
              answer="Yes, you can cancel your subscription at any time. You'll continue to have access until the end of your billing period."
            />
            <FAQItem
              question="What happens if I run out of searches?"
              answer="You can upgrade to a higher plan anytime, or wait for your monthly quota to reset."
            />
            <FAQItem
              question="What payment methods do you accept?"
              answer="We accept all major credit cards, PayPal, and Apple Pay through our secure payment processor."
            />
            <FAQItem
              question="Is there a refund policy?"
              answer="Yes, we offer a 7-day money-back guarantee for first-time subscribers."
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h3 className="font-semibold text-gray-900">{question}</h3>
      <p className="mt-2 text-sm text-gray-600">{answer}</p>
    </div>
  )
}
