# Tesouro TransCost

Dashboard de visualização de custos por itens de pessoal ativo do Governo Federal Brasileiro, com dados do [Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/dataset/custos-por-itens-de-custos-pessoal-ativo).

## Stack

- **[Next.js 16](https://nextjs.org/)** — App Router, Server Components
- **[TypeScript](https://www.typescriptlang.org/)**
- **[Supabase](https://supabase.com/)** — PostgreSQL gerenciado, cache persistente dos dados
- **[Recharts](https://recharts.org/)** — gráficos de evolução mensal e top itens
- **[Tailwind CSS](https://tailwindcss.com/)**
- **[Vercel](https://vercel.com/)** — deploy e hospedagem

## Rodando localmente

**Pré-requisitos:** Node.js 18+

```bash
# 1. Clone e instale dependências
git clone https://github.com/vpdiogo/tesouro-TransCost.git
cd tesouro-TransCost
npm install

# 2. Configure as variáveis de ambiente
cp .env.local.example .env.local
# edite .env.local com suas credenciais do Supabase

# 3. Inicie o servidor de desenvolvimento
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000).

## Configurando o Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. No **SQL Editor**, execute o conteúdo de [`supabase/schema.sql`](./supabase/schema.sql)
3. Copie a **Project URL** e a **anon key** em `Settings → API`
4. Cole no `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://<project>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>
```

## Deploy na Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Importe o repositório na Vercel
2. Adicione as variáveis de ambiente (`NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY`)
3. Deploy automático a cada push na `main`

## Fonte dos dados

API pública do Tesouro Transparente — **Custos por Itens de Custos: Pessoal Ativo**  
`https://www.tesourotransparente.gov.br/ckan/dataset/custos-por-itens-de-custos-pessoal-ativo`
