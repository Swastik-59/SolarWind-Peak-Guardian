import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SolarWind Peak Guardian",
  description: "AI-Powered Hybrid Renewable System for Fossil-Free Evening Peak Management"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
