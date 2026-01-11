import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dig-AI-FTE | Executive Dashboard",
  description: "Real-time monitoring and control center for the autonomous AI employee system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
      </head>
      <body className="antialiased">
        <div className="grid-background"></div>
        {children}
      </body>
    </html>
  );
}
