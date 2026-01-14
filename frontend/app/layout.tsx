import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "./components/Navbar";  // 👈 關鍵就是這一行！一定要有它，樣式才會生效
import BackendWakeup from "./components/BackendWakeup";  // 自動喚醒後端服務

const inter = Inter({ subsets: ["latin"] });

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
      <body className={inter.className}>
        <BackendWakeup />  {/* 頁面載入時喚醒 Render 後端 */}
        <Navbar />
        {children}
      </body>
    </html>
  );
}