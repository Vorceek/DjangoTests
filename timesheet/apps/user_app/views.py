from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.contrib import messages
from django.views import View

from apps.base_app.permissions import aside_icons
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.base_app.permissions import BaseDataMixin

from apps.atividade_app.models import RegistroAtividadeModel
from apps.atividade_app.forms import RegistroAtividadeForm
from apps.atividade_app.views import formatar_duracao
from apps.base_app.models import Periodo

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
class GerenciarAtividadesView(LoginRequiredMixin, BaseDataMixin, View):

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

    def get(self, request):
        user = request.user
        atividades_usuario, page_obj = self.get_atividades_paginadas(user)
        context = self.get_context_data(
            form=RegistroAtividadeForm(),
            page_obj=page_obj,
            total_duracao=self.calcular_total_duracao(atividades_usuario)
        )
        context.update(aside_icons(self.request))
        context['exibir_periodo'] = user.groups.filter(name="PERIODO").exists()
        context['periodos'] = Periodo.objects.all().order_by('nome')
        return render(request, 'user/home.html', context)

    def post(self, request):
        user = request.user
        
        # Finaliza a atividade ativa, se existir, antes de registrar uma nova
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
            atividades_usuario, page_obj = self.get_atividades_paginadas(user)
            context = self.get_context_data(
                form=form,
                page_obj=page_obj,
                total_duracao=self.calcular_total_duracao(atividades_usuario)
            )
            
            context['exibir_periodo'] = user.groups.filter(name="PERIODO").exists()
            context['periodos'] = Periodo.objects.all().order_by('nome')
            return render(request, 'user/home.html', context)