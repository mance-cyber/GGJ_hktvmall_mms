/** @type {import('next').NextConfig} */
const nextConfig = {
  // ==================== 基礎配置 ====================
  reactStrictMode: true,
  swcMinify: true,

  // Docker 部署優化：生成 standalone 輸出，大幅減小鏡像大小
  output: 'standalone',

  // ==================== 圖片優化 ====================
  images: {
    domains: [
      "localhost",
      "hktvmall.com",
      // 根據需要添加其他圖片來源域名
    ],
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // ==================== 實驗性功能 ====================
  experimental: {
    // CSS 優化（需要安裝 critters 套件，暫時停用）
    // optimizeCss: true,
    // 優化套件導入大小
    optimizePackageImports: [
      "lucide-react",
      "recharts",
      "date-fns",
      "@radix-ui/react-dialog",
      "@radix-ui/react-dropdown-menu",
      "@radix-ui/react-select",
    ],
  },

  // ==================== 環境變數 ====================
  env: {
    NEXT_PUBLIC_APP_VERSION: "1.0.0",
  },

  // ==================== 編譯配置 ====================
  compiler: {
    // 移除 console.log（僅生產環境）
    removeConsole:
      process.env.NODE_ENV === "production"
        ? {
            exclude: ["error", "warn"],
          }
        : false,
  },

  // ==================== Headers ====================
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Frame-Options",
            value: "SAMEORIGIN",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
        ],
      },
    ];
  },

  // ==================== 重定向 ====================
  async redirects() {
    return [
      // 根路徑重定向到儀表板（備用，實際由 app/page.tsx 處理）
      // {
      //   source: '/',
      //   destination: '/dashboard',
      //   permanent: false,
      // },
    ];
  },

  // ==================== Webpack 配置 ====================
  webpack: (config, { isServer }) => {
    // 忽略某些警告
    config.ignoreWarnings = [
      { module: /node_modules/ },
    ];

    return config;
  },
};

module.exports = nextConfig;
