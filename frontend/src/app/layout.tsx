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
        {/* Banner superior con logo alineado a la derecha */}
        <div className="w-full bg-[#3E3557] border-b border-[#2e2741]">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <div />
            <img src="/empleadosnet.svg" alt="Empleados.net" className="h-10 md:h-12" />
          </div>
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