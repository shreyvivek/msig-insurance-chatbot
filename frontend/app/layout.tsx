import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'WanderSure - Your Smart Travel Insurance Companion',
  description: 'As easy as chatting with a travel buddy who just happens to know everything about insurance.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}

