import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Conciliador IA - Conciliación Bancaria',
  description: 'Sistema de conciliación automática de extractos bancarios con comprobantes usando IA',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={inter.className}>
        {/* Logo superior flotante (sin barra) */}
        <div className="fixed top-3 right-4 z-50">
          <img
            src="/empleadosnet.svg"
            alt="Empleados.net"
            className="h-7 md:h-9 drop-shadow-sm opacity-95"
          />
        </div>

        {children}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </body>
    </html>
  )
} 