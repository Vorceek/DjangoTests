from django.urls import path
from .endpoints import get_atividades_por_servico, get_servicos_por_cliente, get_servicos_por_atividade
from .views import (
    get_servicos,
    get_atividades,
    ListarAtividadesView,
    RegistrarAtividadeView,
    FinalizarAtividadeView,
    GerenciarAtividadesView,
)


app_name = 'atividade_app'

urlpatterns = [
    # Endpoints AJAX por ID:
    path('ajax/servicos/<int:cliente_id>/', get_servicos, name='get_servicos'),
    path('ajax/atividades/<int:servico_id>/', get_atividades, name='get_atividades'),
    
    # Endpoint AJAX:
    path('get_servicos_por_cliente/', get_servicos_por_cliente, name='get_servicos_por_cliente'),
    path('get_atividades_por_servico/', get_atividades_por_servico, name='get_atividades_por_servico'),
    path('get_servicos_por_atividade/', get_servicos_por_atividade, name='get_servicos_por_atividade'),

    # Views para registro e gerenciamento de atividades
    path('listar/', ListarAtividadesView.as_view(), name='listar_atividades'),
    path('registrar/', RegistrarAtividadeView.as_view(), name='registrar_atividade'),
    path('finalizar/<int:atividade_id>/', FinalizarAtividadeView.as_view(), name='finalizar_atividade'),
    path('gerenciar/', GerenciarAtividadesView.as_view(), name='gerenciar_atividades'),
]
