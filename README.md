# Tesouro TransCost

[![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)

Dashboard de visualização de custos por itens de pessoal ativo do Governo Federal Brasileiro, com dados do [Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/dataset/custos-por-itens-de-custos-pessoal-ativo).

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
