# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 2

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_RAZORPAY_KEY: process.env.NEXT_PUBLIC_RAZORPAY_KEY,
  },
  images: {
    domains: ['images.unsplash.com'],
  },
}

module.exports = nextConfig
