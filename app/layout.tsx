import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import menuData from "../public/menus.json";
import logo from "../public/alvikslunchenyellow.png";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Alvikslunchen",
  description: "Find out what's for lunch in Alvik",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-900 min-h-screen flex flex-col`}
      >
        <header className="bg-zinc-800 text-white p-4 flex items-center">
          <div className="flex-shrink-0">
            <a href="/" aria-label="Homepage">
              <img src={logo.src} alt="Logo" className="h-8 w-auto" />
            </a>
          </div>
          <nav className="ml-4">{/* navigation links */}</nav>
        </header>

        {/* Main content fills available space */}
        <main className="flex-grow">{children}</main>

        {/* ✨ Improved sticky footer (always visible, centered, clean) */}
        <footer
          className="
  fixed bottom-0 left-0 w-full
  bg-zinc-800 text-center text-zinc-400
  py-2 border-t border-zinc-700 text-xs
  z-50
"
        >
          Uppdaterad {menuData.last_updated}
        </footer>
      </body>
    </html>
  );
}
