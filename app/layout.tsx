
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
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-900`}
      >
        <header className="bg-zinc-800 text-white p-4 flex items-center">
          <div className="flex-shrink-0">
            {/* Wrap the logo image in an anchor tag */}
            <a href="/" aria-label="Homepage">
              <img src={logo.src} alt="Logo" className="h-8 w-auto" />
            </a>
          </div>
          <nav className="ml-4">
            {/* Add navigation items here if needed */}
          </nav>
        </header>
        <main className="flex-grow">{children}</main>
        <footer className="text-center text-zinc-600 pb-4 text-sm">
          Uppdaterad {menuData.last_updated}
        </footer>
      </body>
    </html>
  );
}
