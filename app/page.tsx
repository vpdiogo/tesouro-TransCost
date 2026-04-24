import { Suspense } from "react";
import { TrendingDown, DollarSign, Calendar, BarChart2 } from "lucide-react";
import { fetchTesouroData, mapApiRecordToCustoItem } from "@/lib/tesouro/api";
import { StatCard } from "@/components/ui/StatCard";
import { CostEvolutionChart } from "@/components/charts/CostEvolutionChart";
import { TopItemsChart } from "@/components/charts/TopItemsChart";
import type { CustoAgregado, CustoMensal, DashboardStats } from "@/types";

async function getDashboardStats(ano: number): Promise<DashboardStats> {
  const records = await fetchTesouroData(ano);
  const mapped = records.map(mapApiRecordToCustoItem);

  const agregadoPorItem = mapped.reduce<Record<string, number>>((acc, r) => {
    acc[r.item_custo] = (acc[r.item_custo] ?? 0) + r.valor;
    return acc;
  }, {});

  const totalGeral = Object.values(agregadoPorItem).reduce((s, v) => s + v, 0);

  const topItens: CustoAgregado[] = Object.entries(agregadoPorItem)
    .map(([item_custo, total]) => ({
      item_custo,
      total,
      percentual: totalGeral > 0 ? (total / totalGeral) * 100 : 0,
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 8);

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

  return {
    totalGeral,
    totalMesAtual: mesAtual?.total ?? 0,
    variacaoMensal,
    topItens,
    evolucaoMensal,
  };
}

function formatBRL(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

async function Dashboard({ ano }: { ano: number }) {
  const stats = await getDashboardStats(ano);

  return (
    <>
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <StatCard
          title="Total Anual"
          value={formatBRL(stats.totalGeral)}
          subtitle={`Ano ${ano}`}
          icon={<DollarSign size={18} />}
        />
        <StatCard
          title="Último Mês"
          value={formatBRL(stats.totalMesAtual)}
          subtitle={stats.evolucaoMensal.at(-1)?.periodo ?? "—"}
          trend={stats.variacaoMensal}
          icon={<Calendar size={18} />}
        />
        <StatCard
          title="Itens de Custo"
          value={String(stats.topItens.length)}
          subtitle="Categorias identificadas"
          icon={<BarChart2 size={18} />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-800 mb-1">
            Evolução Mensal
          </h2>
          <p className="text-xs text-gray-400 mb-4">Custo total por mês em {ano}</p>
          <CostEvolutionChart data={stats.evolucaoMensal} />
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-800 mb-1">
            Top Itens de Custo
          </h2>
          <p className="text-xs text-gray-400 mb-4">
            Maiores categorias de custo em {ano}
          </p>
          <TopItemsChart data={stats.topItens} />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-800">
            Detalhamento por Item
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left px-6 py-3 font-medium text-gray-500">
                  Item de Custo
                </th>
                <th className="text-right px-6 py-3 font-medium text-gray-500">
                  Total
                </th>
                <th className="text-right px-6 py-3 font-medium text-gray-500">
                  Participação
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {stats.topItens.map((item, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 text-gray-700">{item.item_custo}</td>
                  <td className="px-6 py-4 text-right font-mono text-gray-900">
                    {new Intl.NumberFormat("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    }).format(item.total)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 bg-gray-100 rounded-full h-1.5">
                        <div
                          className="bg-blue-500 h-1.5 rounded-full"
                          style={{ width: `${Math.min(item.percentual, 100)}%` }}
                        />
                      </div>
                      <span className="text-gray-600 tabular-nums w-12 text-right">
                        {item.percentual.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ ano?: string }>;
}) {
  const params = await searchParams;
  const ano = params.ano ? parseInt(params.ano, 10) : new Date().getFullYear();

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TrendingDown className="text-blue-600" size={22} />
            <div>
              <h1 className="text-base font-bold text-gray-900 leading-none">
                Tesouro TransCost
              </h1>
              <p className="text-xs text-gray-400 mt-0.5">
                Custos de Pessoal Ativo — Governo Federal
              </p>
            </div>
          </div>
          <a
            href="https://www.tesourotransparente.gov.br"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-400 hover:text-blue-600 transition-colors"
          >
            Fonte: Tesouro Transparente ↗
          </a>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page title */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900">
            Dashboard de Custos — {ano}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Custos por itens de pessoal ativo do Governo Federal Brasileiro
          </p>
        </div>

        <Suspense
          fallback={
            <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
              Carregando dados do Tesouro Transparente...
            </div>
          }
        >
          <Dashboard ano={ano} />
        </Suspense>
      </div>
    </main>
  );
}
