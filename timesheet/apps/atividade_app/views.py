from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.views import View

from .models import RegistroAtividadeModel, Cliente, Servico, Atividade
from .forms import RegistroAtividadeForm

# ----------------------
# Função para formatar a duração (formato hh:mm:ss)
# ----------------------
def formatar_duracao(total_segundos):
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    segundos = int(total_segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

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
        user = request.user
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


class GerenciarAtividadesView(View):
    def get_context_data(self, user):
        # Agora, usamos os grupos do usuário para filtrar os clientes, serviços e atividades
        setores_usuario = user.groups.all()
        clientes = Cliente.objects.filter(setor__in=setores_usuario).distinct()
        servicos = Servico.objects.filter(setor__in=setores_usuario).distinct()
        atividades = Atividade.objects.filter(setor__in=setores_usuario).distinct()
        is_admin = user.groups.filter(name='Admin').exists()
        return {
            'clientes': clientes,
            'servicos': servicos,
            'atividades': atividades,
            'is_admin': is_admin,
        }

    def calcular_total_duracao(self, atividades_usuario):
        total_segundos = sum(
            (a.RAM_dataFinal - a.RAM_dataInicial).total_seconds()
            for a in atividades_usuario if a.RAM_dataFinal and a.RAM_dataInicial
        )
        return formatar_duracao(total_segundos)

    def get(self, request):
        user = request.user
        context = self.get_context_data(user)
        atividades_usuario = RegistroAtividadeModel.objects.filter(RAM_colaborador=user).order_by('-RAM_dataInicial')
        paginator = Paginator(atividades_usuario, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'form': RegistroAtividadeForm(),
            'page_obj': page_obj,
            'total_duracao': self.calcular_total_duracao(atividades_usuario),
        })
        return render(request, 'home/gerenciar_atividades.html', context)

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
            return redirect('atividade_app:gerenciar_atividades')
        else:
            context = self.get_context_data(user)
            atividades_usuario = RegistroAtividadeModel.objects.filter(RAM_colaborador=user).order_by('-RAM_dataInicial')
            paginator = Paginator(atividades_usuario, 9)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context.update({
                'form': form,
                'page_obj': page_obj,
                'total_duracao': self.calcular_total_duracao(atividades_usuario),
            })
            return render(request, 'home/gerenciar_atividades.html', context)
