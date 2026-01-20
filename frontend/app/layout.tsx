import type { Metadata } from "next";
import { Noto_Sans_TC } from "next/font/google"; // Switch to Noto Sans TC
import "./globals.css";
import Navbar from "./components/Navbar";
import BackendWakeup from "./components/BackendWakeup";
import { LanguageProvider } from "./context/LanguageContext";

const notoSansTC = Noto_Sans_TC({
  subsets: ["latin"],
  weight: ["100", "300", "400", "500", "700", "900"],
  variable: "--font-noto-sans",
});

export const metadata: Metadata = {
  title: "MIRRA War Room",
  description: "Market Intelligence & Reality Rendering Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={notoSansTC.className}>
        <LanguageProvider>
          <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
          <BackendWakeup />
          <Navbar />
          {children}
        </LanguageProvider>
      </body>
    </html>
  );
}