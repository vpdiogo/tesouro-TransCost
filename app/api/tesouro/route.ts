import { NextResponse } from "next/server";
import { fetchTesouroData, mapApiRecordToCustoItem } from "@/lib/tesouro/api";
import { createClient } from "@/lib/supabase/server";
import type { CustoAgregado, CustoMensal, DashboardStats } from "@/types";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const ano = searchParams.get("ano")
    ? parseInt(searchParams.get("ano")!, 10)
    : new Date().getFullYear();

  try {
    const records = await fetchTesouroData(ano);
    const supabase = await createClient();

    const mapped = records.map(mapApiRecordToCustoItem);

    // Upsert no Supabase para cache persistente
    if (mapped.length > 0) {
      await supabase.from("custos").upsert(
        mapped.map((r) => ({
          ...r,
          unique_key: `${r.ano}-${r.mes}-${r.item_custo}-${r.orgao_subordinado_nome}`,
        })),
        { onConflict: "unique_key", ignoreDuplicates: true }
      );
    }

    // Agrega por item de custo
    const agregadoPorItem = mapped.reduce<Record<string, number>>((acc, r) => {
      acc[r.item_custo] = (acc[r.item_custo] ?? 0) + r.valor;
      return acc;
    }, {});

    const totalGeral = Object.values(agregadoPorItem).reduce(
      (s, v) => s + v,
      0
    );

    const topItens: CustoAgregado[] = Object.entries(agregadoPorItem)
      .map(([item_custo, total]) => ({
        item_custo,
        total,
        percentual: totalGeral > 0 ? (total / totalGeral) * 100 : 0,
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10);

    // Agrega por mês
    const agregadoPorMes = mapped.reduce<Record<string, number>>((acc, r) => {
      const key = `${r.ano}-${String(r.mes).padStart(2, "0")}`;
      acc[key] = (acc[key] ?? 0) + r.valor;
      return acc;
    }, {});

    const evolucaoMensal: CustoMensal[] = Object.entries(agregadoPorMes)
      .map(([periodo, total]) => ({ periodo, total }))
      .sort((a, b) => a.periodo.localeCompare(b.periodo));

    const mesAtual = evolucaoMensal.at(-1);
    const mesAnterior = evolucaoMensal.at(-2);
    const variacaoMensal =
      mesAnterior && mesAnterior.total > 0
        ? ((mesAtual!.total - mesAnterior.total) / mesAnterior.total) * 100
        : 0;

    const stats: DashboardStats = {
      totalGeral,
      totalMesAtual: mesAtual?.total ?? 0,
      variacaoMensal,
      topItens,
      evolucaoMensal,
    };

    return NextResponse.json(stats);
  } catch (error) {
    console.error("Erro ao buscar dados do Tesouro:", error);
    return NextResponse.json(
      { error: "Falha ao buscar dados" },
      { status: 500 }
    );
  }
}
