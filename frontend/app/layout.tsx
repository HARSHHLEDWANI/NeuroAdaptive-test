import type { Metadata } from "next";
import { Geist, Geist_Mono, Kodchasan } from "next/font/google";
import AuthProvider from "@/components/AuthProvider";
import "./globals.css"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const kodchasan = Kodchasan({
  variable: "--font-kodchasan",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Neuro Adaptive AI Assistant",
  description: "AI-powered adaptive learning assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${kodchasan.variable} antialiased font-sans bg-gray-50`}
      >
        <AuthProvider>
          {/* 2. Place Navbar inside AuthProvider so it can access user state if needed */}

          {/* 3. Wrap children in a container to provide consistent spacing below the Navbar */}
          <main className="min-h-screen">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
