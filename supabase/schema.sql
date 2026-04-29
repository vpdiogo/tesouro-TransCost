-- Tabela principal de custos
create table if not exists public.custos (
  id            bigserial primary key,
  unique_key    text unique not null,
  ano           integer not null,
  mes           integer not null,
  item_custo    text not null,
  orgao_superior_nome     text not null,
  orgao_subordinado_nome  text not null,
  valor         numeric(18, 2) not null,
  created_at    timestamptz default now()
);

-- Índices para queries comuns
create index if not exists idx_custos_ano on public.custos(ano);
create index if not exists idx_custos_ano_mes on public.custos(ano, mes);
create index if not exists idx_custos_item on public.custos(item_custo);

-- Leitura pública (dados abertos de governo)
alter table public.custos enable row level security;

create policy "Leitura pública"
  on public.custos for select
  using (true);
