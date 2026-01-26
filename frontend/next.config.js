/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // 標記 WebSocket 為外部依賴（僅服務器端）
  webpack: (config, { isServer }) => {
    if (isServer) {
      // 在服務器端構建中，將 ws 標記為外部依賴
      config.externals = [...(config.externals || []), 'ws'];
    }
    return config;
  },

  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return [
      // Clawdbot API 由 Next.js API 路由處理，不代理到後端
      // 其他所有 /api 請求代理到 Python 後端
      {
        source: '/api/v1/((?!scrape/clawdbot).*)',
        destination: `${apiUrl}/api/v1/$1`,
      },
    ]
  },
}

module.exports = nextConfig
