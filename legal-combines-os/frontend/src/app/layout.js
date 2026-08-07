import './globals.css'
import { Inter } from 'next/font/google'
import { Providers } from './providers'


const inter = Inter({ subsets: ['latin'] })


export const metadata = {
  title: 'Legal Combines OS',
  description: 'AI-Powered Global Legal Compliance Platform',
  keywords: 'legal, compliance, AI, document review, marketplace',
  authors: [{ name: 'clickwise-maker' }],
  openGraph: {
    title: 'Legal Combines OS',
    description: 'AI-Powered Global Legal Compliance Platform',
    url: 'https://legal-combines.com',
    siteName: 'Legal Combines OS',
    images: [
      {
        url: 'https://legal-combines.com/og-image.jpg',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Legal Combines OS',
    description: 'AI-Powered Global Legal Compliance Platform',
    images: ['https://legal-combines.com/twitter-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
