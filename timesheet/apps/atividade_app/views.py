from django.db.models.functions import ExtractWeekDay
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin
from apps.base_app.permissions import BaseDataMixin
from apps.base_app.permissions import PaginationMixin

from .models import RegistroAtividadeModel, Cliente, Servico, Atividade
from .forms import RegistroAtividadeForm

# ----------------------
# Função para formatar a duração (formato hh:mm:ss)
# ----------------------
def formatar_duracao(total_segundos):

    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    segundos = int(total_segundos % 60)

    return f"{horas}:{minutos:02d}:{segundos:02d}"

# ----------------------
# Pegar o Grupo do Usuário
# ----------------------
def get_user_groups(user):
    """Retorna os grupos do usuário, excluindo ADMINISTRADOR e USER."""
    return user.groups.exclude(name__in=['ADMINISTRADOR', 'USER'])


# ----------------------
# Endpoints AJAX
# ----------------------
def get_servicos(request, cliente_id):
    """Retorna os serviços associados ao cliente, filtrados pelos grupos do usuário."""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    # Obtém os grupos do usuário (excluindo ADMINISTRADOR e USER)
    user_groups = get_user_groups(request.user)
    
    # Filtra os serviços que pertencem aos grupos do usuário
    servicos = Servico.objects.filter(
        clientes=cliente,
        setor__in=user_groups
    ).distinct()
    
    
    data = {'servicos': [{'id': s.id, 'nome': s.nome} for s in servicos]}
    return JsonResponse(data)

def get_atividades(request, servico_id):
    """Retorna as atividades associadas ao serviço, filtradas pelos grupos do usuário."""
    servico = get_object_or_404(Servico, id=servico_id)
    
    # Obtém os grupos do usuário (excluindo ADMINISTRADOR e USER)
    user_groups = get_user_groups(request.user)
    
    # Filtra as atividades que pertencem aos grupos do usuário
    atividades = Atividade.objects.filter(
        servicos=servico,
        setor__in=user_groups
    ).distinct()
    
    
    data = {'atividades': [{'id': a.id, 'nome': a.nome} for a in atividades]}
    return JsonResponse(data)

# ----------------------
# Handler para finalizar atividades ativas
# ----------------------
class FinalizarAtividadesHandler:
    def __init__(self, user):
        self.user = user

    def finalizar_atividades_ativas(self):
        atividades_ativas = RegistroAtividadeModel.objects.filter(RAM_colaborador=self.user, RAM_ativo=True)
        if atividades_ativas.exists():
            atividade_ativa = atividades_ativas.first()
            atividade_ativa.RAM_dataFinal = now()
            atividade_ativa.RAM_ativo = False
            atividade_ativa.RAM_duracao = atividade_ativa.RAM_dataFinal - atividade_ativa.RAM_dataInicial
            atividade_ativa.save()
            return atividade_ativa
        return None


# ----------------------
# Get Atividades por Dia
# ----------------------
def get_atividades_por_dia_data(setores_dinamicos, data_inicio, data_fim):
    qs = RegistroAtividadeModel.objects.filter(
        RAM_colaborador__groups__name__in=setores_dinamicos,
        RAM_dataInicial__date__gte=data_inicio,
        RAM_dataInicial__date__lte=data_fim
    ).annotate(dia_semana=ExtractWeekDay("RAM_dataInicial")).values("dia_semana")
    atividades_count = {i: 0 for i in range(1, 8)}
    for item in qs:
        dia = item["dia_semana"]
        if dia in atividades_count:
            atividades_count[dia] += 1
    return [atividades_count.get(i, 0) for i in range(1, 8)]

# ----------------------
# Views
# ----------------------

class ListarAtividadesView(View):
    def get(self, request):
        user = request.user
        # Filtra as atividades do usuário (pelo campo RAM_colaborador)
        atividades = RegistroAtividadeModel.objects.filter(RAM_colaborador=user).order_by('-RAM_dataInicial')
        total_segundos = sum(
            (a.RAM_dataFinal - a.RAM_dataInicial).total_seconds()
            for a in atividades if a.RAM_dataFinal and a.RAM_dataInicial
        )
        total_duracao = formatar_duracao(total_segundos)
        paginator = Paginator(atividades, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'home/listar_atividades.html', {
            'page_obj': page_obj,
            'page_number': page_number,
            'total_duracao': total_duracao,
        })


class RegistrarAtividadeView(View):
    def get(self, request):
        # Agora, para filtrar os setores, usamos os grupos do usuário
        setores_usuario = request.user.groups.all()
        clientes = Cliente.objects.filter(setor__in=setores_usuario)
        servicos = Servico.objects.filter(setor__in=setores_usuario)
        atividades = Atividade.objects.filter(setor__in=setores_usuario)
        form = RegistroAtividadeForm()
        return render(request, 'home/registrar_atividade.html', {
            'form': form,
            'clientes': clientes,
            'servicos': servicos,
            'atividades': atividades,
        })

    def post(self, request):
        user = request.user
        # Finaliza atividade ativa (se existir) antes de registrar uma nova
        handler = FinalizarAtividadesHandler(user)
        atividade_ativa = handler.finalizar_atividades_ativas()
        if atividade_ativa:
            messages.success(
                request,
                f'A atividade ativa foi finalizada em {atividade_ativa.RAM_dataFinal.strftime("%d/%m/%Y %H:%M:%S")}'
            )
        form = RegistroAtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.RAM_colaborador = user
            atividade.save()
            return redirect('atividade_app:gerenciar_atividades')
        else:
            setores_usuario = request.user.groups.all()
            clientes = Cliente.objects.filter(setor__in=setores_usuario)
            servicos = Servico.objects.filter(setor__in=setores_usuario)
            atividades = Atividade.objects.filter(setor__in=setores_usuario)
            return render(request, 'home/registrar_atividade.html', {
                'form': form,
                'clientes': clientes,
                'servicos': servicos,
                'atividades': atividades,
            })


class FinalizarAtividadeView(View):
    def post(self, request, atividade_id):
        user = request.user
        atividade = get_object_or_404(RegistroAtividadeModel, id=atividade_id, RAM_colaborador=user)
        atividade.RAM_dataFinal = now()
        atividade.RAM_ativo = False
        atividade.RAM_duracao = atividade.RAM_dataFinal - atividade.RAM_dataInicial
        atividade.save()
        return JsonResponse({
            'success': True,
            'dataFinal': atividade.RAM_dataFinal.strftime('%d/%m/%Y %H:%M'),
        })

    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)


class GerenciarAtividadesView(LoginRequiredMixin, BaseDataMixin, PaginationMixin, View):
    
    def get_atividades_paginadas(self, user):

        atividades_usuario = RegistroAtividadeModel.objects.filter(RAM_colaborador=user).order_by('-RAM_dataInicial')
        paginator = Paginator(atividades_usuario, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return atividades_usuario, page_obj

    def calcular_total_duracao(self, atividades_usuario):

        total_segundos = sum(
            (a.RAM_dataFinal - a.RAM_dataInicial).total_seconds()
            for a in atividades_usuario if a.RAM_dataFinal and a.RAM_dataInicial
        )

        return formatar_duracao(total_segundos)

    def post(self, request):
        user = request.user
        handler = FinalizarAtividadesHandler(user)
        atividade_ativa = handler.finalizar_atividades_ativas()
        if atividade_ativa:
            messages.success(
                request,
                f'A atividade ativa foi finalizada em {atividade_ativa.RAM_dataFinal.strftime("%d/%m/%Y %H:%M:%S")}'
            )
        form = RegistroAtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.RAM_colaborador = user
            atividade.save()
            return redirect('user_app:home')
        else:
            # Obtém o queryset de atividades e pagina os resultados usando o mixin
            atividades_usuario = RegistroAtividadeModel.objects.filter(RAM_colaborador=user).order_by('-RAM_dataInicial')
            paginated_context = self.get_atividades_paginadas(user)
            context = self.get_context_data(
                form=form,
                total_duracao=self.calcular_total_duracao(atividades_usuario)
            )
            context.update(paginated_context)
            return render(request, 'user/home.html', context)