from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.views import View
from django.utils.timezone import now
from apps.atividade_app.models import RegistroAtividadeModel
from apps.base_app.models import Cliente, Servico, Atividade
from apps.atividade_app.forms import RegistroAtividadeForm

# Função para formatar duração no formato 00:00:00
def formatar_duracao(total_segundos):
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    segundos = int(total_segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# Handler para finalizar atividades ativas
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

# View para gerenciar (listar e registrar) atividades
class GerenciarAtividadesView(LoginRequiredMixin, View):
    def get_context_data(self, user):
        grupos_usuario = user.groups.all()
        clientes = Cliente.objects.filter(setor__in=grupos_usuario).distinct().order_by('nome')
        servicos = Servico.objects.filter(setor__in=grupos_usuario).distinct().order_by('nome')
        atividades = Atividade.objects.filter(setor__in=grupos_usuario).distinct().order_by('nome')
        return {
            'clientes': clientes,
            'servicos': servicos,
            'atividades': atividades,
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
        return render(request, 'user/home.html', context)

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
            return render(request, 'user/home.html', context)