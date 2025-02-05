from django.urls import path
from .views import AdminView, GerarRelatorioView

app_name = 'admin_app'

urlpatterns = [
    path('', AdminView.as_view(), name='hub'),
    path('relatorio/', GerarRelatorioView.as_view(), name='gerar_relatorio'),
]
