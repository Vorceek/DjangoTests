from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.base_app.permissions import AdminRequiredMixin, aside_icons
from datetime import datetime
from io import BytesIO
import pandas as pd
import pytz
from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from apps.atividade_app.models import Cliente, RegistroAtividadeModel, Servico, Atividade
from django.contrib.auth.models import User
from django.utils.timezone import make_naive
from django.db.models import Count, Q
import json
import plotly.express as px
from django.contrib.auth.models import User, Group
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models.functions import ExtractWeekDay
from django.utils.timezone import now

class AdminView(LoginRequiredMixin, TemplateView):
    template_name = "admin/hub.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fixed_groups = ["ADMINISTRADOR", "USER"]
        
        # Obtém os setores dinâmicos (grupos que o usuário faz parte, excluindo os fixos)
        setores_dinamicos = list(
            self.request.user.groups.exclude(name__in=fixed_groups).values_list('name', flat=True)
        )

        if not setores_dinamicos:
            context.update({
                'labels': json.dumps([]),
                'values': json.dumps([]),
                'count_trabalhando': 0,
                'count_nao_trabalhando': 0,
                'count_total': 0,
            })
            return context

        try:
            user_group = Group.objects.get(name="USER")
        except Group.DoesNotExist:
            context.update({
                'labels': json.dumps([]),
                'values': json.dumps([]),
                'count_trabalhando': 0,
                'count_nao_trabalhando': 0,
                'count_total': 0,
            })
            return context

        # Filtra as atividades do setor do usuário na semana atual
        atividades = RegistroAtividadeModel.objects.filter(
        RAM_colaborador__groups__name__in=setores_dinamicos,
        RAM_dataInicial__week=now().isocalendar()[1]
        ).annotate(dia_semana=ExtractWeekDay("RAM_dataInicial")).values("dia_semana")

        # Dicionário para contar atividades por dia da semana
        atividades_count = {i: 0 for i in range(2, 8)}  # Segunda (2) até Sábado (7)

        for atividade in atividades:
            dia = atividade["dia_semana"]
            if dia in atividades_count:
                atividades_count[dia] += 1

        # Converte para lista no formato que o JS espera
        atividades_por_dia = [atividades_count.get(i, 0) for i in range(2, 8)]

        # Filtra usuários do mesmo setor e que sejam "USER"
        usuarios_setor = User.objects.filter(groups__name__in=setores_dinamicos).distinct()
        usuarios_regulares = usuarios_setor.filter(groups=user_group).distinct()
        count_total = usuarios_regulares.count()

        # Conta os usuários ativos e inativos
        usuarios_trabalhando = usuarios_regulares.annotate(
            total_ativos=Count('registroatividademodel', filter=Q(registroatividademodel__RAM_ativo=True))
        ).filter(total_ativos__gt=0)
        count_trabalhando = usuarios_trabalhando.count()
        count_nao_trabalhando = count_total - count_trabalhando

        # Envia os dados para o template
        context['labels'] = json.dumps(['Trabalhando', 'Não Trabalhando'])
        context['values'] = json.dumps([count_trabalhando, count_nao_trabalhando])
        context['count_trabalhando'] = count_trabalhando
        context['count_nao_trabalhando'] = count_nao_trabalhando
        context['count_total'] = count_total
        context["atividades_por_dia"] = json.dumps(atividades_por_dia)

        return context


    
# Função para formatar a duração em "hh:mm:ss"
def formatar_duracao(total_segundos):
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    segundos = int(total_segundos % 60)
    return f"{horas}:{minutos:02d}:{segundos:02d}"

class RelatorioHandler:
    @staticmethod
    def criar_pdf(atividades, formatted_total_duracao):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elementos = []
        styles = getSampleStyleSheet()

        data_geracao = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
        elementos.append(Paragraph(f"Data de Geração: {data_geracao}", styles['Normal']))
        elementos.append(Spacer(1, 12))
        titulo_style = styles['Title']
        titulo_style.textColor = colors.HexColor("#007bff")
        elementos.append(Paragraph("Relatório de Atividades", titulo_style))
        elementos.append(Spacer(1, 12))

        cell_style = ParagraphStyle(
            name="cell_style",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=1,
            wordWrap='LTR'
        )

        dados = [['Colaborador', 'Cliente', 'Serviço', 'Atividade', 'Data Inicial', 'Data Final', 'Duração']]
        for atividade in atividades:
            dados.append([
                str(atividade.RAM_colaborador),
                str(atividade.RAM_cliente),
                str(atividade.RAM_servico),
                Paragraph(str(atividade.RAM_atividade), cell_style),
                atividade.RAM_dataInicial.strftime("%d/%m/%Y %H:%M:%S") if atividade.RAM_dataInicial else '0:00:00',
                atividade.RAM_dataFinal.strftime("%d/%m/%Y %H:%M:%S") if atividade.RAM_dataFinal else '0:00:00',
                atividade.duracao_formatada,
            ])

        tabela = Table(dados, colWidths=[70, 70, 100, 100, 90, 90, 70])
        estilo_tabela = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
            ("ALIGN", (0, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ])
        tabela.setStyle(estilo_tabela)
        elementos.append(tabela)
        elementos.append(Spacer(1, 12))

        total_style = styles['Normal']
        total_style.fontName = "Helvetica-Bold"
        total_style.textColor = colors.HexColor("#343a40")
        elementos.append(Paragraph(f'<b>Total de Duração:</b> {formatted_total_duracao}', total_style))

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    @staticmethod
    def exportar_para_excel(atividades):
        # Cria a lista de dados; para as datas, convertemos os datetimes com fuso para naive.
        data = [
            {
                'Colaborador': str(atividade.RAM_colaborador),
                'Cliente': str(atividade.RAM_cliente),
                'Serviço': str(atividade.RAM_servico),
                'Atividade': str(atividade.RAM_atividade),
                'Data Inicial': make_naive(atividade.RAM_dataInicial) if atividade.RAM_dataInicial else pd.NaT,
                'Data Final': make_naive(atividade.RAM_dataFinal) if atividade.RAM_dataFinal else pd.NaT,
                'Duração': atividade.RAM_duracao if atividade.RAM_duracao else pd.Timedelta(0),
            }
            for atividade in atividades
        ]
        
        # Calcula o total de duração em segundos e converte para timedelta
        total_segundos = sum(
            (atividade.RAM_dataFinal - atividade.RAM_dataInicial).total_seconds()
            for atividade in atividades if atividade.RAM_dataFinal and atividade.RAM_dataInicial
        )
        total_duracao = pd.Timedelta(seconds=total_segundos)
        
        # Adiciona a linha do total de duração
        data.append({
            'Colaborador': '',
            'Cliente': '',
            'Serviço': '',
            'Atividade': '',
            'Data Inicial': None,
            'Data Final': 'Total de Duração:',
            'Duração': total_duracao,
        })
        
        df = pd.DataFrame(data)
        
        # Use ExcelWriter com o engine openpyxl
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatorio')
            workbook = writer.book
            worksheet = writer.sheets['Relatorio']
            
            from openpyxl.utils import get_column_letter
            
            # Defina os formatos desejados para as colunas:
            # - Data Inicial e Data Final: formato de data/hora "dd/mm/yyyy hh:mm:ss"
            # - Duração: formato de tempo "[h]:mm:ss"
            formatações = {
                "Data Inicial": "dd/mm/yyyy hh:mm:ss",
                "Data Final": "dd/mm/yyyy hh:mm:ss",
                "Duração": "[h]:mm:ss"
            }
            
            for col_name, num_fmt in formatações.items():
                # Obtenha o índice da coluna (openpyxl é 1-indexado)
                col_idx = df.columns.get_loc(col_name) + 1
                col_letter = get_column_letter(col_idx)
                # Ajusta a largura da coluna (opcional)
                worksheet.column_dimensions[col_letter].width = 20
                # Aplica o formato para todas as células dessa coluna (exceto o cabeçalho)
                for row in range(2, worksheet.max_row + 1):
                    cell = worksheet[f"{col_letter}{row}"]
                    cell.number_format = num_fmt
                    
        buffer.seek(0)
        return buffer

class GerarRelatorioView(LoginRequiredMixin, AdminRequiredMixin, View):
    login_url = "login/"  # URL para redirecionamento se não estiver logado

    def get(self, request, *args, **kwargs):
        # Obtém os grupos (setores) do usuário (usando os grupos do Django)
        setores_usuario = request.user.groups.all()

        # Filtra as atividades cujo cliente pertence a algum desses grupos
        atividades = RegistroAtividadeModel.objects.filter(
            RAM_cliente__setor__in=setores_usuario
        ).distinct()

        # Filtros checkbox
        servico_ids = request.GET.getlist('servico')
        if servico_ids:
            atividades = atividades.filter(RAM_servico__id__in=servico_ids)

        cliente_ids = request.GET.getlist('cliente')
        if cliente_ids:
            atividades = atividades.filter(RAM_cliente__id__in=cliente_ids)

        atividade_ids = request.GET.getlist('atividade')
        if atividade_ids:
            atividades = atividades.filter(RAM_atividade__id__in=atividade_ids)

        colaborador_ids = request.GET.getlist('colaborador')
        if colaborador_ids:
            atividades = atividades.filter(RAM_colaborador__id__in=colaborador_ids)

        # Filtros de data – filtramos pela data de início (RAM_dataInicial)
        hora = request.GET.get('hora')
        data_fim = request.GET.get('data_fim')
        if hora and data_fim:
            try:
                hora_datetime = datetime.strptime(hora, '%Y-%m-%d')
                data_fim_datetime = datetime.strptime(data_fim, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                atividades = atividades.filter(RAM_dataInicial__gte=hora_datetime, RAM_dataInicial__lte=data_fim_datetime)
            except ValueError:
                pass

        atividades = atividades.order_by('-RAM_dataInicial')
        paginator = Paginator(atividades, 20)
        atividades_page = paginator.get_page(request.GET.get('page'))

        total_segundos = sum(
            (a.RAM_dataFinal - a.RAM_dataInicial).total_seconds()
            for a in atividades if a.RAM_dataFinal and a.RAM_dataInicial
        )
        formatted_total_duracao = formatar_duracao(total_segundos)

        # Exportação de PDF ou Excel
        if 'gerar_pdf' in request.GET:
            buffer = RelatorioHandler.criar_pdf(atividades, formatted_total_duracao)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="relatorio_atividades.pdf"'
            return response

        if 'gerar_excel' in request.GET:
            buffer = RelatorioHandler.exportar_para_excel(atividades)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="relatorio_atividades.xlsx"'
            return response

        # Para os filtros exibidos no template, obtemos clientes, serviços, atividades e colaboradores
        clientes = Cliente.objects.filter(setor__in=setores_usuario).distinct()
        servicos = Servico.objects.filter(setor__in=setores_usuario).distinct()
        atividadegeral = Atividade.objects.filter(setor__in=setores_usuario).distinct()
        colaboradores = User.objects.filter(groups__in=setores_usuario).distinct()

        context = {
            'atividades': atividades_page,
            'page_obj': atividades_page,
            'clientes': clientes,
            'servicos': servicos,
            'atividadegeral': atividadegeral,
            'colaboradores': colaboradores,
            'hora': hora,
            'data_fim': data_fim,
            'total_duracao': formatted_total_duracao,
            'is_admin': request.user.groups.filter(name='Admin').exists(),
            'colaborador_ids': request.GET.getlist('colaborador'),
            'cliente_ids': request.GET.getlist('cliente'),
            'servico_ids': request.GET.getlist('servico'),
            'atividadegeral_ids': request.GET.getlist('atividade'),
        }
        context.update(aside_icons(request))
        return render(request, 'admin/relatorio.html', context)

