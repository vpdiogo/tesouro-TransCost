"""Management command para ingestão de dados de custos do Tesouro Nacional."""

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.utils import timezone

from costs.client import DATASETS, TesouroClient
from costs.models import (
    DemaisCustos,
    Depreciacao,
    IngestionLog,
    Orgao,
    Pensionista,
    PessoalAtivo,
    PessoalInativo,
    Transferencia,
)

MODEL_MAP = {
    "pessoal_ativo": PessoalAtivo,
    "pessoal_inativo": PessoalInativo,
    "pensionista": Pensionista,
    "demais_custos": DemaisCustos,
    "depreciacao": Depreciacao,
    "transferencia": Transferencia,
}


def parse_decimal(value):
    """Parse a decimal value from API response, handling Brazilian formatting."""
    if value is None:
        return Decimal("0")
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    value = str(value).strip()
    if not value or value == "-":
        return Decimal("0")
    # Handle Brazilian number format: 1.234.567,89 -> 1234567.89
    value = value.replace(".", "").replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation:
        return Decimal("0")


def parse_int(value):
    """Parse an integer value from API response."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip().replace(".", "").replace(",", ""))
    except (ValueError, TypeError):
        return 0


def extract_year_month(periodo):
    """Extract year and month from periodo string.

    Handles formats like '2023-01', '01/2023', '2023', 'jan/2023', etc.
    """
    if not periodo:
        return None, None
    periodo = str(periodo).strip()

    # Format: 2023-01
    match = re.match(r"(\d{4})-(\d{1,2})", periodo)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Format: 01/2023
    match = re.match(r"(\d{1,2})/(\d{4})", periodo)
    if match:
        return int(match.group(2)), int(match.group(1))

    # Format: just a year
    match = re.match(r"^(\d{4})$", periodo)
    if match:
        return int(match.group(1)), None

    return None, None


def get_or_create_orgao(record):
    """Get or create an Orgao from a record dict."""
    # Try common field names for organ code/name
    codigo = (
        record.get("co_orgao")
        or record.get("codigo_orgao")
        or record.get("CodigoOrgao")
        or record.get("cd_orgao")
        or record.get("Orgao")
        or "DESCONHECIDO"
    )
    nome = (
        record.get("no_orgao")
        or record.get("nome_orgao")
        or record.get("NomeOrgao")
        or record.get("ds_orgao")
        or record.get("Orgao")
        or str(codigo)
    )
    codigo = str(codigo).strip()
    nome = str(nome).strip()
    orgao, _ = Orgao.objects.get_or_create(codigo=codigo, defaults={"nome": nome})
    return orgao


def get_field(record, *field_names, default=""):
    """Get the first matching field from a record."""
    for name in field_names:
        if name in record and record[name] is not None:
            return str(record[name]).strip()
    return default


def build_pessoal_record(record, orgao, periodo, ano, mes):
    """Build common fields for pessoal ativo/inativo/pensionista."""
    return {
        "periodo": periodo,
        "ano": ano,
        "mes": mes,
        "orgao": orgao,
        "unidade_organizacional": get_field(
            record, "no_unidade_organizacional", "UnidadeOrganizacional",
            "unidade_organizacional", "ds_unidade_organizacional",
        ),
        "area_atuacao": get_field(
            record, "no_area_atuacao", "AreaAtuacao", "area_atuacao", "ds_area_atuacao",
        ),
        "escolaridade": get_field(
            record, "no_escolaridade", "Escolaridade", "escolaridade", "ds_escolaridade",
        ),
        "sexo": get_field(record, "no_sexo", "Sexo", "sexo", "ds_sexo"),
        "faixa_etaria": get_field(
            record, "no_faixa_etaria", "FaixaEtaria", "faixa_etaria", "ds_faixa_etaria",
        ),
        "forca_trabalho": parse_int(
            record.get("qt_forca_trabalho")
            or record.get("ForcaTrabalho")
            or record.get("forca_trabalho")
            or record.get("qt_ft")
        ),
        "custo": parse_decimal(
            record.get("vl_custo")
            or record.get("Custo")
            or record.get("custo")
            or record.get("valor")
        ),
    }


def record_to_model_kwargs(dataset_key, record):
    """Convert an API record dict to model field kwargs."""
    periodo = get_field(
        record, "periodo", "Periodo", "no_periodo", "ds_periodo", "Mes",
    )
    ano_raw = record.get("ano") or record.get("Ano") or record.get("nu_ano")
    if ano_raw:
        ano = parse_int(ano_raw)
    else:
        ano, _ = extract_year_month(periodo)
    _, mes = extract_year_month(periodo)
    if not ano:
        ano = 0

    orgao = get_or_create_orgao(record)

    if dataset_key in ("pessoal_ativo", "pessoal_inativo", "pensionista"):
        return build_pessoal_record(record, orgao, periodo, ano, mes)

    if dataset_key == "demais_custos":
        return {
            "periodo": periodo,
            "ano": ano,
            "mes": mes,
            "orgao": orgao,
            "centro_custo": get_field(
                record, "no_centro_custo", "CentroCusto", "centro_custo", "ds_centro_custo",
            ),
            "item_custo": get_field(
                record, "no_item_custo", "ItemCusto", "item_custo", "ds_item_custo",
            ),
            "custo": parse_decimal(
                record.get("vl_custo") or record.get("Custo") or record.get("custo")
            ),
        }

    if dataset_key == "depreciacao":
        return {
            "periodo": periodo,
            "ano": ano,
            "mes": mes,
            "orgao": orgao,
            "conta_contabil": get_field(
                record, "no_conta_contabil", "ContaContabil", "conta_contabil",
                "ds_conta_contabil",
            ),
            "custo": parse_decimal(
                record.get("vl_custo") or record.get("Custo") or record.get("custo")
            ),
        }

    if dataset_key == "transferencia":
        return {
            "periodo": periodo,
            "ano": ano,
            "mes": mes,
            "orgao": orgao,
            "esfera_orcamentaria": get_field(
                record, "no_esfera_orcamentaria", "EsferaOrcamentaria",
                "esfera_orcamentaria", "ds_esfera_orcamentaria",
            ),
            "modalidade_aplicacao": get_field(
                record, "no_modalidade_aplicacao", "ModalidadeAplicacao",
                "modalidade_aplicacao", "ds_modalidade_aplicacao",
            ),
            "resultado_eof": get_field(
                record, "no_resultado_eof", "ResultadoEOF", "resultado_eof",
                "ds_resultado_eof",
            ),
            "custo": parse_decimal(
                record.get("vl_custo") or record.get("Custo") or record.get("custo")
            ),
        }

    raise ValueError(f"Unknown dataset: {dataset_key}")


class Command(BaseCommand):
    help = "Ingestão de dados de custos do Tesouro Nacional"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            choices=list(DATASETS.keys()) + ["all"],
            default="all",
            help="Dataset para ingestão (default: all)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Limpar dados existentes antes da ingestão",
        )

    def handle(self, *args, **options):
        dataset_key = options["dataset"]
        clear = options["clear"]

        datasets = list(DATASETS.keys()) if dataset_key == "all" else [dataset_key]

        for ds in datasets:
            self._ingest_dataset(ds, clear=clear)

    def _ingest_dataset(self, dataset_key, clear=False):
        model = MODEL_MAP[dataset_key]
        log = IngestionLog.objects.create(dataset=dataset_key)

        self.stdout.write(f"Ingerindo {dataset_key}...")

        try:
            if clear:
                deleted, _ = model.objects.all().delete()
                self.stdout.write(f"  Removidos {deleted} registros existentes.")

            client = TesouroClient()
            records_fetched = 0
            records_created = 0
            batch = []
            batch_size = 500

            for record in client.fetch_all_pages(dataset_key):
                records_fetched += 1
                try:
                    kwargs = record_to_model_kwargs(dataset_key, record)
                    batch.append(model(**kwargs))
                except Exception as exc:
                    self.stderr.write(f"  Erro ao processar registro: {exc}")
                    continue

                if len(batch) >= batch_size:
                    model.objects.bulk_create(batch, ignore_conflicts=True)
                    records_created += len(batch)
                    batch = []
                    self.stdout.write(f"  {records_fetched} registros processados...")

            if batch:
                model.objects.bulk_create(batch, ignore_conflicts=True)
                records_created += len(batch)

            log.records_fetched = records_fetched
            log.records_created = records_created
            log.success = True
            log.finished_at = timezone.now()
            log.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"  {dataset_key}: {records_fetched} fetched, {records_created} created."
                )
            )

        except Exception as exc:
            log.error_message = str(exc)
            log.finished_at = timezone.now()
            log.save()
            self.stderr.write(self.style.ERROR(f"  Erro em {dataset_key}: {exc}"))
