import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "家族健康管理アプリ",
  description: "家族全員の健康データを一つのダッシュボードで管理。Fitbitデータ連携とAI健康アドバイス機能付き。",
  keywords: ["健康管理", "家族", "Fitbit", "ダッシュボード", "ヘルスケア"],
  authors: [{ name: "Family Health Team" }],
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja" className="dark">
      <body className={`${inter.className} antialiased bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen`}>
        <div className="flex flex-col min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}