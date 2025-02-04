from django.urls import path
from .views import AdminView, gerar_relatorio

app_name = 'admin_app'

urlpatterns = [
    path('', AdminView.as_view(), name='hub'),
    path('relatorio/', gerar_relatorio, name='gerar_relatorio'),
]
