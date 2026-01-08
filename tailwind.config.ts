import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // ==================== 色彩系統 ====================
      colors: {
        // 品牌主色
        brand: {
          primary: {
            50: "#EBF5FF",
            100: "#D1E9FF",
            200: "#B3DDFF",
            300: "#84CAFF",
            400: "#53B1FD",
            500: "#2E90FA",
            600: "#1570EF",
            700: "#175CD3",
            800: "#1849A9",
            900: "#194185",
            DEFAULT: "#1570EF",
          },
          secondary: {
            50: "#F0F3FF",
            100: "#E0E7FF",
            200: "#C7D2FE",
            300: "#A5B4FC",
            400: "#818CF8",
            500: "#6366F1",
            600: "#4F46E5",
            700: "#4338CA",
            800: "#3730A3",
            900: "#312E81",
            DEFAULT: "#4F46E5",
          },
        },

        // 功能色
        success: {
          50: "#ECFDF5",
          100: "#D1FAE5",
          200: "#A7F3D0",
          300: "#6EE7B7",
          400: "#34D399",
          500: "#10B981",
          600: "#059669",
          700: "#047857",
          800: "#065F46",
          900: "#064E3B",
          DEFAULT: "#10B981",
        },
        warning: {
          50: "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          300: "#FCD34D",
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",
          700: "#B45309",
          800: "#92400E",
          900: "#78350F",
          DEFAULT: "#F59E0B",
        },
        error: {
          50: "#FEF2F2",
          100: "#FEE2E2",
          200: "#FECACA",
          300: "#FCA5A5",
          400: "#F87171",
          500: "#EF4444",
          600: "#DC2626",
          700: "#B91C1C",
          800: "#991B1B",
          900: "#7F1D1D",
          DEFAULT: "#EF4444",
        },
        info: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          200: "#BFDBFE",
          300: "#93C5FD",
          400: "#60A5FA",
          500: "#3B82F6",
          600: "#2563EB",
          700: "#1D4ED8",
          800: "#1E40AF",
          900: "#1E3A8A",
          DEFAULT: "#3B82F6",
        },

        // 圖表配色
        chart: {
          blue: "#2E90FA",
          purple: "#7C3AED",
          teal: "#14B8A6",
          orange: "#F97316",
          pink: "#EC4899",
          green: "#10B981",
          red: "#EF4444",
          amber: "#F59E0B",
        },

        // 中性色（擴展灰階）
        gray: {
          50: "#F9FAFB",
          100: "#F3F4F6",
          200: "#E5E7EB",
          300: "#D1D5DB",
          400: "#9CA3AF",
          500: "#6B7280",
          600: "#4B5563",
          700: "#374151",
          800: "#1F2937",
          900: "#111827",
          950: "#030712",
        },

        // shadcn/ui 兼容性
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },

      // ==================== 字型系統 ====================
      fontFamily: {
        sans: [
          "Noto Sans TC",
          "PingFang TC",
          "Microsoft JhengHei",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "SF Mono",
          "Consolas",
          "Liberation Mono",
          "Menlo",
          "monospace",
        ],
        numeric: ["Roboto Mono", "SF Mono", "monospace"],
      },

      fontSize: {
        // Display
        "display-2xl": ["72px", { lineHeight: "90px", fontWeight: "700" }],
        "display-xl": ["60px", { lineHeight: "72px", fontWeight: "700" }],
        "display-lg": ["48px", { lineHeight: "60px", fontWeight: "700" }],

        // Heading
        h1: ["36px", { lineHeight: "44px", fontWeight: "700" }],
        h2: ["30px", { lineHeight: "38px", fontWeight: "600" }],
        h3: ["24px", { lineHeight: "32px", fontWeight: "600" }],
        h4: ["20px", { lineHeight: "28px", fontWeight: "600" }],
        h5: ["18px", { lineHeight: "26px", fontWeight: "500" }],

        // Body
        xl: ["20px", { lineHeight: "30px" }],
        lg: ["18px", { lineHeight: "28px" }],
        base: ["16px", { lineHeight: "24px" }],
        sm: ["14px", { lineHeight: "20px" }],
        xs: ["12px", { lineHeight: "18px" }],

        // Caption
        caption: ["11px", { lineHeight: "16px" }],
      },

      fontWeight: {
        light: "300",
        regular: "400",
        medium: "500",
        semibold: "600",
        bold: "700",
      },

      // ==================== 間距系統 ====================
      spacing: {
        0: "0px",
        1: "4px",
        2: "8px",
        3: "12px",
        4: "16px",
        5: "20px",
        6: "24px",
        8: "32px",
        10: "40px",
        12: "48px",
        16: "64px",
        20: "80px",
        24: "96px",
      },

      // ==================== 圓角系統 ====================
      borderRadius: {
        none: "0px",
        sm: "4px",
        DEFAULT: "6px",
        base: "6px",
        md: "8px",
        lg: "12px",
        xl: "16px",
        "2xl": "24px",
        full: "9999px",
      },

      // ==================== 陰影系統 ====================
      boxShadow: {
        xs: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        sm: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
        DEFAULT:
          "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
        md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
        lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
        xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
        "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        inner: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)",
        outline: "0 0 0 3px rgba(46, 144, 250, 0.5)",
        "outline-error": "0 0 0 3px rgba(239, 68, 68, 0.5)",
      },

      // ==================== 動畫系統 ====================
      transitionDuration: {
        instant: "100ms",
        fast: "150ms",
        DEFAULT: "200ms",
        base: "200ms",
        slow: "300ms",
        slower: "500ms",
      },

      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0, 0, 0.2, 1)",
        linear: "linear",
        in: "cubic-bezier(0.4, 0, 1, 1)",
        out: "cubic-bezier(0, 0, 0.2, 1)",
        "in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
        bounce: "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
      },

      // ==================== 斷點系統 ====================
      screens: {
        xs: "480px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px",
      },

      // ==================== 漸變色 ====================
      backgroundImage: {
        "gradient-cool":
          "linear-gradient(135deg, #667EEA 0%, #764BA2 100%)",
        "gradient-warm":
          "linear-gradient(135deg, #F093FB 0%, #F5576C 100%)",
        "gradient-success":
          "linear-gradient(135deg, #4ADE80 0%, #22C55E 100%)",
        "gradient-primary":
          "linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%)",
      },

      // ==================== 其他擴展 ====================
      zIndex: {
        dropdown: "1000",
        sticky: "1020",
        fixed: "1030",
        "modal-backdrop": "1040",
        modal: "1050",
        popover: "1060",
        tooltip: "1070",
      },

      // 動畫關鍵幀
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "fade-out": {
          "0%": { opacity: "1" },
          "100%": { opacity: "0" },
        },
        "slide-in-up": {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "slide-in-down": {
          "0%": { transform: "translateY(-10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "scale-in": {
          "0%": { transform: "scale(0.95)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },

      animation: {
        "fade-in": "fade-in 200ms ease-out",
        "fade-out": "fade-out 200ms ease-out",
        "slide-in-up": "slide-in-up 200ms ease-out",
        "slide-in-down": "slide-in-down 200ms ease-out",
        "scale-in": "scale-in 150ms ease-out",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
