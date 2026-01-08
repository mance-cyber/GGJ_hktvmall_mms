# Implementation Plan - Phase 1: Visual DNA (Sci-Fi Light Theme)

## Goal
Transform the core visual system into a "Light Mode Sci-Fi/Lab" aesthetic.
Target files: `app/layout.tsx`, `tailwind.config.ts`, `app/globals.css`.

## Step 1: Install Fonts & Configure Layout
**File:** `app/layout.tsx`

**Changes:**
1.  Import `Space_Grotesk` and `JetBrains_Mono` from `next/font/google`.
2.  Configure them with `variable` property.
3.  Add the variable classes to the `<body>` tag.

**Code Snippet:**
```tsx
import { Noto_Sans_TC, Space_Grotesk, JetBrains_Mono } from "next/font/google";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

// In RootLayout:
<body className={`${notoSansTC.className} ${spaceGrotesk.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
```

## Step 2: Update Design Tokens
**File:** `tailwind.config.ts`

**Changes:**
1.  Extend `colors` with the `sci` palette.
2.  Extend `fontFamily` to use the CSS variables.
3.  Add `glow`, `scan`, `pulse-slow` animations.

**Sci-Fi Palette:**
- `sci-base`: `#F0F4F8` (Ice Silver Background)
- `sci-card`: `rgba(255, 255, 255, 0.7)` (Glass)
- `sci-cyan`: `#06B6D4` (Primary Accents)
- `sci-purple`: `#8B5CF6` (Secondary Accents)
- `sci-text`: `#0F172A` (Deep Blue Black)

**Animation Keyframes:**
```ts
keyframes: {
  "glow-pulse": {
    "0%, 100%": { boxShadow: "0 0 5px rgba(6, 182, 212, 0.2)" },
    "50%": { boxShadow: "0 0 20px rgba(6, 182, 212, 0.6)" },
  },
  "scanline": {
    "0%": { transform: "translateY(-100%)" },
    "100%": { transform: "translateY(100%)" },
  }
}
```

## Step 3: Global Styles & Atmosphere
**File:** `app/globals.css`

**Changes:**
1.  Define the CSS variables for the fonts if needed (Next.js handles this, but we map them).
2.  Create the **Living Grid** background in `body`.
3.  Create `.glass-panel` utility class.

**Living Grid CSS:**
```css
body {
  background-color: #F0F4F8;
  background-image: 
    linear-gradient(rgba(6, 182, 212, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(6, 182, 212, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  background-position: center top;
}
```

## Step 4: Component Primitives
**Action:** Create a new folder `components/sci-fi`.
**Components:**
1.  `HoloCard.tsx`: A wrapper around Shadcn Card with specific sci-fi styling.
2.  `TechButton.tsx`: A button with glitch/glow effects.

