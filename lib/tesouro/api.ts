import type { TesouroApiRecord, TesouroApiResponse, CustoItem } from "@/types";

const TESOURO_API_BASE =
  "https://apidatalake.tesouro.gov.br/ords/custos/tt/pessoal_ativo";

export async function fetchTesouroData(
  ano?: number,
  limit = 1000,
  offset = 0
): Promise<TesouroApiRecord[]> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  if (ano) {
    params.set("an_lanc", String(ano));
  }

  const url = `${TESOURO_API_BASE}?${params.toString()}`;
  const res = await fetch(url, { next: { revalidate: 3600 } });

  if (!res.ok) {
    throw new Error(`Tesouro API error: ${res.status}`);
  }

  const data: TesouroApiResponse = await res.json();
  return data.items;
}

export function mapApiRecordToCustoItem(
  record: TesouroApiRecord
): Omit<CustoItem, "id" | "created_at"> {
  return {
    ano: record.an_lanc,
    mes: record.me_lanc,
    item_custo: record.ds_area_atuacao,
    orgao_superior_nome: record.ds_organizacao_n1,
    orgao_subordinado_nome: record.ds_organizacao_n2,
    valor: record.va_custo_de_pessoal,
  };
}
