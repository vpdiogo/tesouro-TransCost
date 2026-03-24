import json
import statistics
from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, TemplateView

from .models import (
    DemaisCustos,
    Depreciacao,
    IngestionLog,
    Orgao,
    Pensionista,
    PessoalAtivo,
    PessoalInativo,
    Transferencia,
)


class DashboardView(TemplateView):
    template_name = "costs/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Summary stats
        ctx["total_orgaos"] = Orgao.objects.count()
        ctx["total_pessoal_ativo"] = PessoalAtivo.objects.aggregate(t=Sum("custo"))["t"] or 0
        ctx["total_pessoal_inativo"] = PessoalInativo.objects.aggregate(t=Sum("custo"))["t"] or 0
        ctx["total_pensionistas"] = Pensionista.objects.aggregate(t=Sum("custo"))["t"] or 0
        ctx["total_demais"] = DemaisCustos.objects.aggregate(t=Sum("custo"))["t"] or 0
        ctx["total_depreciacao"] = Depreciacao.objects.aggregate(t=Sum("custo"))["t"] or 0
        ctx["total_transferencias"] = Transferencia.objects.aggregate(t=Sum("custo"))["t"] or 0

        ctx["total_geral"] = sum(
            [
                ctx["total_pessoal_ativo"],
                ctx["total_pessoal_inativo"],
                ctx["total_pensionistas"],
                ctx["total_demais"],
                ctx["total_depreciacao"],
                ctx["total_transferencias"],
            ]
        )

        # Available years
        years = set()
        for model in [PessoalAtivo, PessoalInativo, Pensionista, DemaisCustos, Depreciacao, Transferencia]:
            model_years = model.objects.values_list("ano", flat=True).distinct()
            years.update(model_years)
        ctx["anos"] = sorted(y for y in years if y > 0)

        # Top 10 órgãos by cost
        ctx["top_orgaos"] = (
            PessoalAtivo.objects.values("orgao__id", "orgao__nome").annotate(total=Sum("custo")).order_by("-total")[:10]
        )

        # Last ingestion
        ctx["last_ingestion"] = IngestionLog.objects.first()

        return ctx


class OrgaoDetailView(DetailView):
    model = Orgao
    template_name = "costs/orgao_detail.html"
    context_object_name = "orgao"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orgao = self.object

        # Costs by year for this organ
        custo_por_ano = defaultdict(lambda: Decimal("0"))
        for model, label in [
            (PessoalAtivo, "pessoal_ativo"),
            (PessoalInativo, "pessoal_inativo"),
            (Pensionista, "pensionista"),
        ]:
            qs = model.objects.filter(orgao=orgao).values("ano").annotate(total=Sum("custo"))
            for row in qs:
                custo_por_ano[row["ano"]] += row["total"]

        ctx["custo_por_ano"] = json.dumps(
            sorted(
                [{"ano": k, "total": float(v)} for k, v in custo_por_ano.items() if k > 0],
                key=lambda x: x["ano"],
            )
        )

        # Workforce by year
        ft_por_ano = (
            PessoalAtivo.objects.filter(orgao=orgao).values("ano").annotate(total=Sum("forca_trabalho")).order_by("ano")
        )
        ctx["ft_por_ano"] = json.dumps([{"ano": r["ano"], "total": r["total"]} for r in ft_por_ano if r["ano"] > 0])

        # Demographics breakdown
        ctx["por_escolaridade"] = list(
            PessoalAtivo.objects.filter(orgao=orgao)
            .exclude(escolaridade="")
            .values("escolaridade")
            .annotate(total=Sum("custo"), qtd=Sum("forca_trabalho"))
            .order_by("-total")[:10]
        )

        ctx["por_sexo"] = list(
            PessoalAtivo.objects.filter(orgao=orgao)
            .exclude(sexo="")
            .values("sexo")
            .annotate(total=Sum("custo"), qtd=Sum("forca_trabalho"))
            .order_by("-total")
        )

        ctx["por_faixa_etaria"] = list(
            PessoalAtivo.objects.filter(orgao=orgao)
            .exclude(faixa_etaria="")
            .values("faixa_etaria")
            .annotate(total=Sum("custo"), qtd=Sum("forca_trabalho"))
            .order_by("faixa_etaria")
        )

        # Ratio ativo/inativo/pensionista
        ctx["custo_ativo"] = PessoalAtivo.objects.filter(orgao=orgao).aggregate(t=Sum("custo"))["t"] or 0
        ctx["custo_inativo"] = PessoalInativo.objects.filter(orgao=orgao).aggregate(t=Sum("custo"))["t"] or 0
        ctx["custo_pensionista"] = Pensionista.objects.filter(orgao=orgao).aggregate(t=Sum("custo"))["t"] or 0

        return ctx


class CompararView(TemplateView):
    template_name = "costs/comparar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orgaos"] = Orgao.objects.all()

        orgao_ids = self.request.GET.getlist("orgao")
        if orgao_ids:
            orgaos = Orgao.objects.filter(id__in=orgao_ids)
            comparison = []
            for orgao in orgaos:
                data = (
                    PessoalAtivo.objects.filter(orgao=orgao).values("ano").annotate(total=Sum("custo")).order_by("ano")
                )
                comparison.append(
                    {
                        "nome": orgao.nome,
                        "data": [{"ano": r["ano"], "total": float(r["total"])} for r in data if r["ano"] > 0],
                    }
                )
            ctx["comparison_data"] = json.dumps(comparison)
            ctx["selected_orgaos"] = orgao_ids

        return ctx


class AnomaliasView(TemplateView):
    template_name = "costs/anomalias.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Detect anomalies: organs where latest year cost deviates > 2 std devs from mean
        anomalias = []
        orgaos = Orgao.objects.all()

        for orgao in orgaos:
            custos_por_ano = list(
                PessoalAtivo.objects.filter(orgao=orgao, ano__gt=0)
                .values("ano")
                .annotate(total=Sum("custo"))
                .order_by("ano")
            )
            if len(custos_por_ano) < 3:
                continue

            values = [float(r["total"]) for r in custos_por_ano]
            mean = statistics.mean(values)
            if mean == 0:
                continue
            stdev = statistics.stdev(values)
            if stdev == 0:
                continue

            latest = custos_por_ano[-1]
            z_score = (float(latest["total"]) - mean) / stdev

            if abs(z_score) > 2:
                anomalias.append(
                    {
                        "orgao": orgao,
                        "ano": latest["ano"],
                        "custo": latest["total"],
                        "media": Decimal(str(round(mean, 2))),
                        "z_score": round(z_score, 2),
                        "tipo": "ACIMA" if z_score > 0 else "ABAIXO",
                    }
                )

        ctx["anomalias"] = sorted(anomalias, key=lambda x: abs(x["z_score"]), reverse=True)
        return ctx


# JSON API endpoints for charts


@cache_page(60 * 15)
def custo_por_ano_json(request):
    """Custo total por ano, separado por categoria."""
    result = {}
    for model, label in [
        (PessoalAtivo, "Pessoal Ativo"),
        (PessoalInativo, "Pessoal Inativo"),
        (Pensionista, "Pensionistas"),
        (DemaisCustos, "Demais Custos"),
        (Depreciacao, "Depreciação"),
        (Transferencia, "Transferências"),
    ]:
        data = model.objects.filter(ano__gt=0).values("ano").annotate(total=Sum("custo")).order_by("ano")
        result[label] = [{"ano": r["ano"], "total": float(r["total"])} for r in data]

    return JsonResponse(result)


@cache_page(60 * 15)
def custo_por_categoria_json(request):
    """Custo total por categoria (último ano disponível)."""
    ano = request.GET.get("ano")
    categories = []
    for model, label in [
        (PessoalAtivo, "Pessoal Ativo"),
        (PessoalInativo, "Pessoal Inativo"),
        (Pensionista, "Pensionistas"),
        (DemaisCustos, "Demais Custos"),
        (Depreciacao, "Depreciação"),
        (Transferencia, "Transferências"),
    ]:
        qs = model.objects.all()
        if ano:
            qs = qs.filter(ano=int(ano))
        total = qs.aggregate(t=Sum("custo"))["t"] or 0
        categories.append({"categoria": label, "total": float(total)})

    return JsonResponse({"categories": categories})


@cache_page(60 * 15)
def orgao_ranking_json(request):
    """Top 20 órgãos por custo total de pessoal."""
    ano = request.GET.get("ano")
    qs = PessoalAtivo.objects.all()
    if ano:
        qs = qs.filter(ano=int(ano))
    ranking = qs.values("orgao__nome").annotate(total=Sum("custo")).order_by("-total")[:20]
    return JsonResponse({"ranking": [{"nome": r["orgao__nome"], "total": float(r["total"])} for r in ranking]})


@cache_page(60 * 15)
def orgao_evolucao_json(request, orgao_id):
    """Evolução de custos de um órgão ao longo dos anos."""
    result = {}
    for model, label in [
        (PessoalAtivo, "Pessoal Ativo"),
        (PessoalInativo, "Pessoal Inativo"),
        (Pensionista, "Pensionistas"),
    ]:
        data = (
            model.objects.filter(orgao_id=orgao_id, ano__gt=0)
            .values("ano")
            .annotate(total=Sum("custo"))
            .order_by("ano")
        )
        result[label] = [{"ano": r["ano"], "total": float(r["total"])} for r in data]

    return JsonResponse(result)
