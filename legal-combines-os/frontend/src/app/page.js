# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 2

import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-600 to-indigo-700">
        <div className="max-w-4xl mx-auto px-4 text-center text-white">
          <h1 className="text-5xl font-bold mb-6">
            Legal Combines OS
          </h1>
          <p className="text-xl mb-8 opacity-90">
            AI-powered legal compliance platform for India
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/auth/login"
              className="px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100"
            >
              Sign In
            </Link>
            <Link
              href="/auth/register"
              className="px-8 py-3 bg-transparent border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10"
            >
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl bg-gray-50">
              <h3 className="text-xl font-semibold mb-3">AI Legal Research</h3>
              <p className="text-gray-600">Automated legal research powered by AI</p>
            </div>
            <div className="p-6 rounded-xl bg-gray-50">
              <h3 className="text-xl font-semibold mb-3">Document Review</h3>
              <p className="text-gray-600">Smart document analysis and compliance checking</p>
            </div>
            <div className="p-6 rounded-xl bg-gray-50">
              <h3 className="text-xl font-semibold mb-3">Expert Marketplace</h3>
              <p className="text-gray-600">Connect with verified lawyers and typists</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
