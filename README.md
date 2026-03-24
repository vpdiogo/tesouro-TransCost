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

## Quick Start

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env

# 2. Subir com Docker
docker compose up -d

# 3. Rodar migrações
docker compose exec web python manage.py migrate

# 4. Ingerir dados (todos os datasets)
docker compose exec web python manage.py ingest_costs

# 5. Acessar
open http://localhost:8000
```

## Desenvolvimento Local (sem Docker)

```bash
# Requisitos: Python 3.12, PostgreSQL, Redis
pip install -r requirements.txt
cd gov_costs
python manage.py migrate
python manage.py ingest_costs --dataset pessoal_ativo
python manage.py runserver
```

## Ingestão de Dados

```bash
# Todos os datasets
python manage.py ingest_costs

# Dataset específico
python manage.py ingest_costs --dataset pessoal_ativo

# Limpar e reingerir
python manage.py ingest_costs --dataset pessoal_ativo --clear
```

Datasets disponíveis: `pessoal_ativo`, `pessoal_inativo`, `pensionista`, `demais_custos`, `depreciacao`, `transferencia`

## Testes

```bash
cd gov_costs
DJANGO_SETTINGS_MODULE=gov_costs.settings_test python manage.py test costs -v2
```

## Celery (ingestão automática)

O Celery Beat pode ser configurado via Django Admin para agendar ingestões periódicas.

```bash
# Worker
celery -A gov_costs worker -l info

# Beat (scheduler)
celery -A gov_costs beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
