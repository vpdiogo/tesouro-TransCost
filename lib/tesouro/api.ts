import type { TesouroApiRecord, TesouroApiResponse, CustoItem } from "@/types";

const TESOURO_API_BASE =
  "https://www.tesourotransparente.gov.br/ckan/api/3/action/datastore_search";

const RESOURCE_ID = "b2dd03ee-3960-4c49-99bf-7b23c7fe1eb0";

export async function fetchTesouroData(
  ano?: number,
  limit = 1000,
  offset = 0
): Promise<TesouroApiRecord[]> {
  const params = new URLSearchParams({
    resource_id: RESOURCE_ID,
    limit: String(limit),
    offset: String(offset),
  });

  if (ano) {
    params.set("filters", JSON.stringify({ ID_ANO_LANC: String(ano) }));
  }

  const url = `${TESOURO_API_BASE}?${params.toString()}`;
  const res = await fetch(url, { next: { revalidate: 3600 } });

  if (!res.ok) {
    throw new Error(`Tesouro API error: ${res.status}`);
  }

  const data: TesouroApiResponse = await res.json();
  return data.result.records;
}

export function mapApiRecordToCustoItem(
  record: TesouroApiRecord
): Omit<CustoItem, "id" | "created_at"> {
  return {
    ano: parseInt(record.ID_ANO_LANC, 10),
    mes: parseInt(record.ID_MES_LANC, 10),
    item_custo: record.NO_ITEM_INFORMACAO,
    orgao_superior_nome: record.NO_ORGAO_SUPERIOR,
    orgao_subordinado_nome: record.NO_ORGAO_SUBORDINADO,
    valor: parseFloat(record.VL_CUSTO.replace(",", ".")),
  };
}
