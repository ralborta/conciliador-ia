/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://conciliador-ia-production.up.railway.app/api/:path*",
      },
    ];
  },
}

module.exports = nextConfig 