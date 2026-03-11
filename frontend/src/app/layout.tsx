import type { Metadata, Viewport } from 'next'
import './globals.css'
import { QueryProvider } from '@/components/QueryProvider'
import { AppShell } from '@/components/AppShell'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'GoGoJap AI Operations System',
  description: 'Competitor Monitor & Price Tracking Dashboard',
  icons: {
    icon: '/favicon.ico',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover', // Support iPhone notch screens
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-50">
        <QueryProvider>
          <AppShell>
            {children}
          </AppShell>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  )
}
