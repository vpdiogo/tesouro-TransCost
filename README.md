# TransCost — Raio-X dos Custos Federais

Dashboard de análise dos custos do governo federal brasileiro, consumindo 6 APIs públicas do Tesouro Nacional. O sistema ingere dados mensais, detecta anomalias de gasto e permite comparação entre órgãos.

## Features

- **Dashboard** — Visão geral com custo total, composição por categoria e ranking de órgãos
- **Detalhe por Órgão** — Evolução temporal, força de trabalho, distribuição por escolaridade/sexo/faixa etária, proporção ativo/inativo/pensionista
- **Comparação** — Comparar evolução de custos entre órgãos
- **Detecção de Anomalias** — Z-score para identificar gastos fora do padrão

## Datasets

| Dataset | Descrição |
|---|---|
| Pessoal Ativo | Custos e headcount de servidores ativos |
| Pessoal Inativo | Custos de aposentados |
| Pensionistas | Custos de pensionistas |
| Demais Custos | TI, materiais, previdência, etc. |
| Depreciação | Depreciação de ativos |
| Transferências | Repasses por modalidade |

Fonte: [Tesouro Transparente — CKAN](https://www.tesourotransparente.gov.br/ckan/dataset)

## Stack

- **Backend:** Django 5.1, Celery, django-celery-beat
- **Banco de dados:** PostgreSQL 16
- **Cache/Broker:** Redis 7
- **Frontend:** Django Templates, Chart.js
- **Infra:** Docker Compose
- **CI:** GitHub Actions (testes + lint com ruff)
- **Package manager:** uv

## Quick Start

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir com Docker
docker compose up -d

# 3. Rodar migrações
docker compose exec web uv run python manage.py migrate

# 4. Ingerir dados (todos os datasets)
docker compose exec web uv run python manage.py ingest_costs

# 5. Acessar
open http://localhost:8000
```

## Desenvolvimento Local (sem Docker)

```bash
# Requisitos: Python 3.12, PostgreSQL, Redis, uv
uv sync
cd gov_costs
uv run python manage.py migrate
uv run python manage.py ingest_costs --dataset pessoal_ativo
uv run python manage.py runserver
```

## Ingestão de Dados

```bash
# Todos os datasets
uv run python manage.py ingest_costs

# Dataset específico
uv run python manage.py ingest_costs --dataset pessoal_ativo

# Limpar e reingerir
uv run python manage.py ingest_costs --dataset pessoal_ativo --clear
```

Datasets disponíveis: `pessoal_ativo`, `pessoal_inativo`, `pensionista`, `demais_custos`, `depreciacao`, `transferencia`

## Testes

```bash
cd gov_costs
DJANGO_SETTINGS_MODULE=gov_costs.settings_test uv run python manage.py test costs -v2
```

## Celery (ingestão automática)

O Celery Beat pode ser configurado via Django Admin para agendar ingestões periódicas.

```bash
# Worker
uv run celery -A gov_costs worker -l info

# Beat (scheduler)
uv run celery -A gov_costs beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
