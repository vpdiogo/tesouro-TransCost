from django.db import models


class Orgao(models.Model):
    """Órgão do governo federal."""

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Órgão"
        verbose_name_plural = "Órgãos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class PessoalAtivo(models.Model):
    """Custos com pessoal ativo do governo federal."""

    periodo = models.CharField(max_length=20)
    ano = models.IntegerField(db_index=True)
    mes = models.IntegerField(null=True, blank=True)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name="pessoal_ativo")
    unidade_organizacional = models.CharField(max_length=300, blank=True, default="")
    area_atuacao = models.CharField(max_length=200, blank=True, default="")
    escolaridade = models.CharField(max_length=100, blank=True, default="")
    sexo = models.CharField(max_length=20, blank=True, default="")
    faixa_etaria = models.CharField(max_length=50, blank=True, default="")
    forca_trabalho = models.IntegerField(default=0)
    custo = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Pessoal Ativo"
        verbose_name_plural = "Pessoal Ativo"
        indexes = [
            models.Index(fields=["ano", "orgao"]),
        ]

    def __str__(self):
        return f"{self.orgao} - {self.periodo}"


class PessoalInativo(models.Model):
    """Custos com pessoal inativo (aposentados)."""

    periodo = models.CharField(max_length=20)
    ano = models.IntegerField(db_index=True)
    mes = models.IntegerField(null=True, blank=True)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name="pessoal_inativo")
    unidade_organizacional = models.CharField(max_length=300, blank=True, default="")
    area_atuacao = models.CharField(max_length=200, blank=True, default="")
    escolaridade = models.CharField(max_length=100, blank=True, default="")
    sexo = models.CharField(max_length=20, blank=True, default="")
    faixa_etaria = models.CharField(max_length=50, blank=True, default="")
    forca_trabalho = models.IntegerField(default=0)
    custo = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Pessoal Inativo"
        verbose_name_plural = "Pessoal Inativo"
        indexes = [
            models.Index(fields=["ano", "orgao"]),
        ]

    def __str__(self):
        return f"{self.orgao} - {self.periodo}"


class Pensionista(models.Model):
    """Custos com pensionistas."""

    periodo = models.CharField(max_length=20)
    ano = models.IntegerField(db_index=True)
    mes = models.IntegerField(null=True, blank=True)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name="pensionistas")
    unidade_organizacional = models.CharField(max_length=300, blank=True, default="")
    area_atuacao = models.CharField(max_length=200, blank=True, default="")
    escolaridade = models.CharField(max_length=100, blank=True, default="")
    sexo = models.CharField(max_length=20, blank=True, default="")
    faixa_etaria = models.CharField(max_length=50, blank=True, default="")
    forca_trabalho = models.IntegerField(default=0)
    custo = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Pensionista"
        verbose_name_plural = "Pensionistas"
        indexes = [
            models.Index(fields=["ano", "orgao"]),
        ]

    def __str__(self):
        return f"{self.orgao} - {self.periodo}"


class DemaisCustos(models.Model):
    """Demais custos operacionais (TI, materiais, etc.)."""

    periodo = models.CharField(max_length=20)
    ano = models.IntegerField(db_index=True)
    mes = models.IntegerField(null=True, blank=True)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name="demais_custos")
    centro_custo = models.CharField(max_length=300, blank=True, default="")
    item_custo = models.CharField(max_length=300, blank=True, default="")
    custo = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Demais Custos"
        verbose_name_plural = "Demais Custos"
        indexes = [
            models.Index(fields=["ano", "orgao"]),
        ]

    def __str__(self):
        return f"{self.orgao} - {self.periodo}"


class Depreciacao(models.Model):
    """Custos de depreciação de ativos."""

    periodo = models.CharField(max_length=20)
    ano = models.IntegerField(db_index=True)
    mes = models.IntegerField(null=True, blank=True)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name="depreciacoes")
    conta_contabil = models.CharField(max_length=300, blank=True, default="")
    custo = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Depreciação"
        verbose_name_plural = "Depreciações"
        indexes = [
            models.Index(fields=["ano", "orgao"]),
        ]

    def __str__(self):
        return f"{self.orgao} - {self.periodo}"


class Transferencia(models.Model):
    """Custos de transferências."""

    periodo = models.CharField(max_length=20)
    ano = models.IntegerField(db_index=True)
    mes = models.IntegerField(null=True, blank=True)
    orgao = models.ForeignKey(Orgao, on_delete=models.CASCADE, related_name="transferencias")
    esfera_orcamentaria = models.CharField(max_length=200, blank=True, default="")
    modalidade_aplicacao = models.CharField(max_length=200, blank=True, default="")
    resultado_eof = models.CharField(max_length=200, blank=True, default="")
    custo = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Transferência"
        verbose_name_plural = "Transferências"
        indexes = [
            models.Index(fields=["ano", "orgao"]),
        ]

    def __str__(self):
        return f"{self.orgao} - {self.periodo}"


class IngestionLog(models.Model):
    """Log de ingestão de dados."""

    dataset = models.CharField(max_length=50)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    records_fetched = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        status = "OK" if self.success else "FAIL"
        return f"{self.dataset} @ {self.started_at:%Y-%m-%d %H:%M} [{status}]"
