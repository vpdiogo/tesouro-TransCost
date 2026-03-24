from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.urls import reverse

from costs.client import TesouroClient, DATASETS
from costs.management.commands.ingest_costs import (
    parse_decimal,
    parse_int,
    extract_year_month,
    record_to_model_kwargs,
)
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


class ParseDecimalTest(TestCase):
    def test_none(self):
        self.assertEqual(parse_decimal(None), Decimal("0"))

    def test_integer(self):
        self.assertEqual(parse_decimal(1000), Decimal("1000"))

    def test_float(self):
        self.assertEqual(parse_decimal(1234.56), Decimal("1234.56"))

    def test_brazilian_format(self):
        self.assertEqual(parse_decimal("1.234.567,89"), Decimal("1234567.89"))

    def test_empty_string(self):
        self.assertEqual(parse_decimal(""), Decimal("0"))

    def test_dash(self):
        self.assertEqual(parse_decimal("-"), Decimal("0"))


class ParseIntTest(TestCase):
    def test_none(self):
        self.assertEqual(parse_int(None), 0)

    def test_integer(self):
        self.assertEqual(parse_int(42), 42)

    def test_string_number(self):
        self.assertEqual(parse_int("1.234"), 1234)


class ExtractYearMonthTest(TestCase):
    def test_iso_format(self):
        self.assertEqual(extract_year_month("2023-01"), (2023, 1))

    def test_br_format(self):
        self.assertEqual(extract_year_month("01/2023"), (2023, 1))

    def test_year_only(self):
        self.assertEqual(extract_year_month("2023"), (2023, None))

    def test_empty(self):
        self.assertEqual(extract_year_month(""), (None, None))

    def test_none(self):
        self.assertEqual(extract_year_month(None), (None, None))


class OrgaoModelTest(TestCase):
    def test_str(self):
        orgao = Orgao.objects.create(codigo="001", nome="Ministério da Fazenda")
        self.assertEqual(str(orgao), "Ministério da Fazenda")


class PessoalAtivoModelTest(TestCase):
    def test_str(self):
        orgao = Orgao.objects.create(codigo="001", nome="Ministério da Fazenda")
        pa = PessoalAtivo.objects.create(
            periodo="2023-01", ano=2023, mes=1, orgao=orgao,
            forca_trabalho=100, custo=Decimal("1000000.00"),
        )
        self.assertIn("Ministério da Fazenda", str(pa))


class IngestionLogModelTest(TestCase):
    def test_str(self):
        log = IngestionLog.objects.create(dataset="pessoal_ativo", success=True)
        self.assertIn("pessoal_ativo", str(log))
        self.assertIn("OK", str(log))


class RecordToModelKwargsTest(TestCase):
    def test_pessoal_ativo(self):
        record = {
            "periodo": "2023-06",
            "ano": 2023,
            "co_orgao": "26000",
            "no_orgao": "Ministério da Educação",
            "no_escolaridade": "Superior",
            "no_sexo": "Masculino",
            "no_faixa_etaria": "30-39",
            "qt_forca_trabalho": 500,
            "vl_custo": "1.234.567,89",
            "no_unidade_organizacional": "UO Teste",
            "no_area_atuacao": "Educação",
        }
        kwargs = record_to_model_kwargs("pessoal_ativo", record)
        self.assertEqual(kwargs["ano"], 2023)
        self.assertEqual(kwargs["custo"], Decimal("1234567.89"))
        self.assertEqual(kwargs["forca_trabalho"], 500)
        self.assertIsInstance(kwargs["orgao"], Orgao)

    def test_demais_custos(self):
        record = {
            "periodo": "2023-06",
            "ano": 2023,
            "co_orgao": "26000",
            "no_orgao": "Ministério da Educação",
            "no_centro_custo": "Centro TI",
            "no_item_custo": "Licenças de Software",
            "vl_custo": "500000,00",
        }
        kwargs = record_to_model_kwargs("demais_custos", record)
        self.assertEqual(kwargs["centro_custo"], "Centro TI")
        self.assertEqual(kwargs["item_custo"], "Licenças de Software")

    def test_depreciacao(self):
        record = {
            "periodo": "2023",
            "ano": 2023,
            "co_orgao": "26000",
            "no_orgao": "Ministério da Educação",
            "no_conta_contabil": "Imóveis",
            "vl_custo": "100000,00",
        }
        kwargs = record_to_model_kwargs("depreciacao", record)
        self.assertEqual(kwargs["conta_contabil"], "Imóveis")

    def test_transferencia(self):
        record = {
            "periodo": "2023",
            "ano": 2023,
            "co_orgao": "26000",
            "no_orgao": "Ministério da Educação",
            "no_esfera_orcamentaria": "Federal",
            "no_modalidade_aplicacao": "Transferência a Municípios",
            "no_resultado_eof": "Resultado X",
            "vl_custo": "2.000.000,00",
        }
        kwargs = record_to_model_kwargs("transferencia", record)
        self.assertEqual(kwargs["esfera_orcamentaria"], "Federal")
        self.assertEqual(kwargs["modalidade_aplicacao"], "Transferência a Municípios")


class DashboardViewTest(TestCase):
    def test_empty_dashboard(self):
        response = self.client.get(reverse("costs:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum dado ingerido")

    def test_dashboard_with_data(self):
        orgao = Orgao.objects.create(codigo="001", nome="Teste")
        PessoalAtivo.objects.create(
            periodo="2023-01", ano=2023, mes=1, orgao=orgao,
            custo=Decimal("1000000"),
        )
        response = self.client.get(reverse("costs:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teste")


class OrgaoDetailViewTest(TestCase):
    def test_detail_page(self):
        orgao = Orgao.objects.create(codigo="001", nome="Teste")
        PessoalAtivo.objects.create(
            periodo="2023-01", ano=2023, mes=1, orgao=orgao,
            custo=Decimal("1000000"), forca_trabalho=100,
        )
        response = self.client.get(reverse("costs:orgao_detail", args=[orgao.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teste")


class AnomaliasViewTest(TestCase):
    def test_empty(self):
        response = self.client.get(reverse("costs:anomalias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhuma anomalia")


class CompararViewTest(TestCase):
    def test_empty(self):
        response = self.client.get(reverse("costs:comparar"))
        self.assertEqual(response.status_code, 200)

    def test_with_selection(self):
        orgao = Orgao.objects.create(codigo="001", nome="Teste")
        PessoalAtivo.objects.create(
            periodo="2023-01", ano=2023, mes=1, orgao=orgao, custo=Decimal("1000000"),
        )
        response = self.client.get(reverse("costs:comparar"), {"orgao": [orgao.id]})
        self.assertEqual(response.status_code, 200)


class JsonEndpointsTest(TestCase):
    def test_custo_por_ano(self):
        response = self.client.get(reverse("costs:custo_por_ano"))
        self.assertEqual(response.status_code, 200)

    def test_custo_por_categoria(self):
        response = self.client.get(reverse("costs:custo_por_categoria"))
        self.assertEqual(response.status_code, 200)

    def test_orgao_ranking(self):
        response = self.client.get(reverse("costs:orgao_ranking"))
        self.assertEqual(response.status_code, 200)

    def test_orgao_evolucao(self):
        orgao = Orgao.objects.create(codigo="001", nome="Teste")
        response = self.client.get(reverse("costs:orgao_evolucao", args=[orgao.id]))
        self.assertEqual(response.status_code, 200)


class TesouroClientTest(TestCase):
    @patch("costs.client.TesouroClient._request")
    def test_get_resource_url(self, mock_request):
        mock_request.return_value = {
            "result": {
                "resources": [
                    {"url": "https://example.com/data.json", "format": "JSON"},
                ]
            }
        }
        client = TesouroClient()
        url = client._get_resource_url("test-slug")
        self.assertEqual(url, "https://example.com/data.json")

    @patch("costs.client.TesouroClient._request")
    @patch("costs.client.TesouroClient._get_resource_url")
    def test_fetch_dataset(self, mock_resource, mock_request):
        mock_resource.return_value = "https://example.com/data.json"
        mock_request.return_value = [{"key": "value"}]
        client = TesouroClient()
        result = client.fetch_dataset("pessoal_ativo", page=1)
        self.assertEqual(result, [{"key": "value"}])
