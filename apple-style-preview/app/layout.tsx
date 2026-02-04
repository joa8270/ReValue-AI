import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MIRRA - Apple Style Preview",
  description: "Apple-style UI preview for MIRRA platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
