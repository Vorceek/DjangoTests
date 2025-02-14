from django.http import JsonResponse
from .models import Cliente, Servico, Atividade

def get_servicos_por_cliente(request):
    cliente_ids = request.GET.getlist('cliente_ids')  # IDs dos clientes selecionados
    servicos = Servico.objects.filter(clientes__id__in=cliente_ids).distinct()
    
    servicos_data = [{"id": servico.id, "nome": servico.nome} for servico in servicos]
    
    return JsonResponse({"servicos": servicos_data})

def get_atividades_por_servico(request):
    servico_ids = request.GET.getlist('servico_ids')  # IDs dos serviços selecionados
    atividades = Atividade.objects.filter(servicos__id__in=servico_ids).distinct()
    
    atividades_data = [{"id": atividade.id, "nome": atividade.nome} for atividade in atividades]
    
    return JsonResponse({"atividades": atividades_data})

def get_servicos_por_atividade(request):
    atividade_ids = request.GET.getlist('atividade_ids')  # IDs das atividades selecionadas
    servicos = Servico.objects.filter(atividades__id__in=atividade_ids).distinct()
    
    servicos_data = [{"id": servico.id, "nome": servico.nome} for servico in servicos]
    
    return JsonResponse({"servicos": servicos_data})

