import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ops Mesh Hospital Management",
  description: "Hospital Operations Management System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="bg-white border-b border-gray-200">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-8">
                <Link href="/" className="text-xl font-bold text-blue-600">
                  🏥 Ops Mesh
                </Link>
                <div className="hidden md:flex space-x-6">
                  <Link href="/" className="text-gray-600 hover:text-blue-600">
                    Home
                  </Link>
                  <Link href="/hospital" className="text-gray-600 hover:text-blue-600">
                    Hospital View
                  </Link>
                  <Link href="/tablet" className="text-gray-600 hover:text-blue-600">
                    Tablet View
                  </Link>
                  <Link href="/live-dashboard" className="text-gray-600 hover:text-blue-600">
                    Live Dashboard
                  </Link>
                  <Link href="/patient-flow" className="text-gray-600 hover:text-blue-600">
                    Patient Flow
                  </Link>
                  <Link href="/test-connection" className="text-gray-600 hover:text-blue-600">
                    Test Connection
                  </Link>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-500">
                  Backend: <span className="text-green-600 font-medium">Connected</span>
                </div>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
      </body>
    </html>
  );
}