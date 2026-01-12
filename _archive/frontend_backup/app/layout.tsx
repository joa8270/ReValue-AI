import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";  // 👈 關鍵就是這一行！一定要有它，樣式才會生效

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
      <body className={inter.className}>{children}</body>
    </html>
  );
}