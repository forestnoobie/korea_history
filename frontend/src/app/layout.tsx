import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "한국사 능력검정시험 퀴즈",
  description: "Korean History Qualification Exam Quiz",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
