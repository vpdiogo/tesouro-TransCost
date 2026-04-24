import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tesouro TransCost — Custos de Pessoal Ativo",
  description:
    "Dashboard de custos por itens de pessoal ativo do Governo Federal Brasileiro. Dados do Tesouro Transparente.",
  openGraph: {
    title: "Tesouro TransCost",
    description: "Visualização de custos de pessoal ativo do Governo Federal",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
