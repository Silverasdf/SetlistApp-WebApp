import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "SetlistApp", description: "Build and export a setlist from your song catalog." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
