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
  items: TesouroApiRecord[];
  hasMore: boolean;
  limit: number;
  offset: number;
  count: number;
}

export interface TesouroApiRecord {
  an_lanc: number;
  me_lanc: number;
  ds_area_atuacao: string;
  ds_organizacao_n1: string;
  ds_organizacao_n2: string;
  va_custo_de_pessoal: number;
}

export interface DashboardStats {
  totalGeral: number;
  totalMesAtual: number;
  variacaoMensal: number;
  topItens: CustoAgregado[];
  evolucaoMensal: CustoMensal[];
}
