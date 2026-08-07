'use client'


import Link from 'next/link'
import { motion } from 'framer-motion'
import { FaScaleBalanced, FaShield, FaRocket, FaUsers } from 'react-icons/fa6'


export default function Home() {
  const features = [
    {
      icon: FaScaleBalanced,
      title: 'AI Legal Analysis',
      description: 'Document review, compliance scoring, and risk assessment powered by DeepSeek AI.'
    },
    {
      icon: FaShield,
      title: 'Compliance Automation',
      description: 'Auto-fill government forms, track deadlines, and stay compliant with 99% accuracy.'
    },
    {
      icon: FaUsers,
      title: 'Legal Marketplace',
      description: 'Connect with verified lawyers and typists. 12% commission, transparent pricing.'
    },
    {
      icon: FaRocket,
      title: 'Global Reach',
      description: 'Multi-language support, 80+ jurisdictions, and real-time government scheme alerts.'
    }
  ]


  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Legal Combines OS
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-4">
            AI-Powered Global Legal Compliance Platform
          </p>
          <p className="text-lg text-gray-500 mb-8">
            Deep Edition — System Initialized Successfully
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/login"
              className="bg-blue-600 text-white px-8 py-4 rounded-xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl text-lg font-medium"
            >
              Get Started
            </Link>
            <Link
              href="/auth/register"
              className="bg-white text-gray-800 px-8 py-4 rounded-xl hover:bg-gray-50 transition-all border border-gray-200 text-lg font-medium"
            >
              Create Account
            </Link>
          </div>
        </motion.div>


        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16 max-w-6xl mx-auto"
        >
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-gray-100"
            >
              <feature.icon className="text-3xl text-blue-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </motion.div>
      </section>
    </main>
  )
}
