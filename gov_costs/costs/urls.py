from django.urls import path

from . import views

app_name = "costs"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("orgao/<int:pk>/", views.OrgaoDetailView.as_view(), name="orgao_detail"),
    path("comparar/", views.CompararView.as_view(), name="comparar"),
    path("anomalias/", views.AnomaliasView.as_view(), name="anomalias"),
    # HTMX endpoints
    path("api/custo-por-ano/", views.custo_por_ano_json, name="custo_por_ano"),
    path("api/custo-por-categoria/", views.custo_por_categoria_json, name="custo_por_categoria"),
    path("api/orgao-ranking/", views.orgao_ranking_json, name="orgao_ranking"),
    path("api/orgao-evolucao/<int:orgao_id>/", views.orgao_evolucao_json, name="orgao_evolucao"),
]
