export interface CustoItem {
  id: number;
  ano: number;
  mes: number;
  item_custo: string;
  orgao_superior_nome: string;
  orgao_subordinado_nome: string;
  valor: number;
  created_at: string;
}

export interface CustoAgregado {
  item_custo: string;
  total: number;
  percentual: number;
}

export interface CustoMensal {
  periodo: string; // "YYYY-MM"
  total: number;
}

export interface TesouroApiResponse {
  result: {
    records: TesouroApiRecord[];
    total: number;
    offset: number;
    limit: number;
  };
}

export interface TesouroApiRecord {
  ID_ANO_LANC: string;
  ID_MES_LANC: string;
  NO_ITEM_INFORMACAO: string;
  NO_ORGAO_SUPERIOR: string;
  NO_ORGAO_SUBORDINADO: string;
  VL_CUSTO: string;
}

export interface DashboardStats {
  totalGeral: number;
  totalMesAtual: number;
  variacaoMensal: number;
  topItens: CustoAgregado[];
  evolucaoMensal: CustoMensal[];
}
