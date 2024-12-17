# tesouro-TransCost

Este projeto utiliza Django, PostgreSQL e Elasticsearch para consultar dados da API pública do governo federal https://www.tesourotransparente.gov.br/ckan/dataset/custos-por-itens-de-custos-pessoal-ativo, para extrair dados e criar visualizações de dados de custo e despesas do governo.

## Requisitos

- Python 3.12
- PostgreSQL
- pipenv

## Passos de Instalação

### 1. Instalar Dependências

Certifique-se de que o Python 3.12 está instalado no seu sistema. Se não estiver, você pode instalá-lo usando os seguintes comandos:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

### 2. Configurar o Ambiente Virtual

No diretório do seu projeto, execute os seguintes comandos para criar e ativar um ambiente virtual com Python 3.12 usando `pipenv`:

```bash
export PIPENV_VENV_IN_PROJECT=1
pipenv --python 3.12
pipenv install django psycopg2-binary
pipenv shell
```

### 3. Configurar o Banco de Dados PostgreSQL

Acesse o PostgreSQL e crie o banco de dados e o usuário:

```bash
sudo -u postgres psql
```

No prompt do PostgreSQL, execute os seguintes comandos (substitua `nome_do_banco_de_dados`, `seu_usuario` e `sua_senha` pelas suas credenciais):

```sql
CREATE DATABASE gov_costs;
CREATE USER admin WITH PASSWORD 'XXXXXX';
ALTER ROLE admin SET client_encoding TO 'utf8';
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gov_costs TO admin;
\c gov_costs
GRANT ALL PRIVILEGES ON SCHEMA public TO admin;
\q
```

### 4. Configurar o Django

No arquivo `settings.py` do seu projeto Django, configure o banco de dados PostgreSQL:

```python
# filepath: /.../tesouro-TransCost/gov_costs/gov_costs/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gov_costs',
        'USER': 'admin',
        'PASSWORD': 'XXXXXX',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Migrar o Banco de Dados

Execute as migrações iniciais do Django para configurar as tabelas padrão:

```bash
python manage.py migrate
```

### 6. Criar um Superusuário

Crie um superusuário para acessar o admin do Django:

```bash
python manage.py createsuperuser
```

### 7. Executar o Servidor de Desenvolvimento

Inicie o servidor de desenvolvimento do Django para verificar se tudo está funcionando corretamente:

```bash
python manage.py runserver
```
