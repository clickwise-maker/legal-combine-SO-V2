# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 2

import './globals.css'

export const metadata = {
  title: 'Legal Combines OS',
  description: 'AI-powered legal compliance platform for India',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <main>{children}</main>
      </body>
    </html>
  )
}
