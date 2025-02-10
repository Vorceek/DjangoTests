from django.urls import path
from apps.admin_app.planinha import exportar_hierarquia_para_excel
from .views import AdminView, GerarRelatorioView

app_name = 'admin_app'

urlpatterns = [
    path('', AdminView.as_view(), name='hub'),
    path('relatorio/', GerarRelatorioView.as_view(), name='gerar_relatorio'),
    path("exportar-hierarquia/", exportar_hierarquia_para_excel, name="exportar_hierarquia"),
]
