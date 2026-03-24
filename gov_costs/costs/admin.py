from django.contrib import admin

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


@admin.register(Orgao)
class OrgaoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome")
    search_fields = ("codigo", "nome")


class BaseCustoAdmin(admin.ModelAdmin):
    list_display = ("orgao", "periodo", "ano", "custo")
    list_filter = ("ano",)
    search_fields = ("orgao__nome",)
    raw_id_fields = ("orgao",)


@admin.register(PessoalAtivo)
class PessoalAtivoAdmin(BaseCustoAdmin):
    list_display = ("orgao", "periodo", "ano", "escolaridade", "sexo", "forca_trabalho", "custo")


@admin.register(PessoalInativo)
class PessoalInativoAdmin(BaseCustoAdmin):
    pass


@admin.register(Pensionista)
class PensionistaAdmin(BaseCustoAdmin):
    pass


@admin.register(DemaisCustos)
class DemaisCustosAdmin(BaseCustoAdmin):
    list_display = ("orgao", "periodo", "ano", "item_custo", "custo")


@admin.register(Depreciacao)
class DepreciacaoAdmin(BaseCustoAdmin):
    list_display = ("orgao", "periodo", "ano", "conta_contabil", "custo")


@admin.register(Transferencia)
class TransferenciaAdmin(BaseCustoAdmin):
    list_display = ("orgao", "periodo", "ano", "modalidade_aplicacao", "custo")


@admin.register(IngestionLog)
class IngestionLogAdmin(admin.ModelAdmin):
    list_display = ("dataset", "started_at", "finished_at", "records_fetched", "records_created", "success")
    list_filter = ("dataset", "success")
