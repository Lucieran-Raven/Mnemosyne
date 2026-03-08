/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
    domains: ['img.clerk.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://api.mnemosyne.dev',
  },
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  devIndicators: {
    buildActivity: false,
    buildActivityPosition: 'bottom-right',
  },
}

module.exports = nextConfig
