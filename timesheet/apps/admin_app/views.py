from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.base_app.permissions import AdminRequiredMixin
from datetime import datetime
from io import BytesIO
import pandas as pd
import pytz
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.timezone import now
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from apps.atividade_app.models import Cliente, RegistroAtividadeModel, Servico, Atividade
from django.contrib.auth.models import User

class AdminView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "admin/hub.html"

# Função para formatar a duração em "hh:mm:ss"
def formatar_duracao(total_segundos):
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    segundos = int(total_segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

class RelatorioHandler:
    @staticmethod
    def criar_pdf(atividades, formatted_total_duracao):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elementos = []
        styles = getSampleStyleSheet()

        # Data de geração
        data_geracao = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
        elementos.append(Paragraph(f"Data de Geração: {data_geracao}", styles['Normal']))
        elementos.append(Spacer(1, 12))

        # Título
        titulo_style = styles['Title']
        titulo_style.textColor = colors.HexColor("#007bff")
        elementos.append(Paragraph("Relatório de Atividades", titulo_style))
        elementos.append(Spacer(1, 12))

        # Estilo para células
        cell_style = ParagraphStyle(
            name="cell_style",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=1,
            wordWrap='LTR'
        )

        # Dados da tabela
        dados = [['Colaborador', 'Cliente', 'Serviço', 'Atividade', 'Data Inicial', 'Data Final', 'Duração']]
        for atividade in atividades:
            dados.append([
                str(atividade.RAM_colaborador),
                str(atividade.RAM_cliente),
                str(atividade.RAM_servico),
                Paragraph(str(atividade.RAM_atividade), cell_style),
                atividade.RAM_dataInicial.strftime("%d/%m/%Y %H:%M:%S") if atividade.RAM_dataInicial else 'N/A',
                atividade.RAM_dataFinal.strftime("%d/%m/%Y %H:%M:%S") if atividade.RAM_dataFinal else 'N/A',
                str(atividade.RAM_duracao) if atividade.RAM_duracao else 'N/A',
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
        data = [
            {
                'Colaborador': str(atividade.RAM_colaborador),
                'Cliente': str(atividade.RAM_cliente),
                'Serviço': str(atividade.RAM_servico),
                'Atividade': str(atividade.RAM_atividade),
                'Data Inicial': atividade.RAM_dataInicial.strftime("%d/%m/%Y %H:%M:%S") if atividade.RAM_dataInicial else 'N/A',
                'Data Final': atividade.RAM_dataFinal.strftime("%d/%m/%Y %H:%M:%S") if atividade.RAM_dataFinal else 'N/A',
                'Duração': str(atividade.RAM_duracao) if atividade.RAM_duracao else 'N/A',
            }
            for atividade in atividades
        ]
        total_segundos = sum(
            (atividade.RAM_dataFinal - atividade.RAM_dataInicial).total_seconds()
            for atividade in atividades if atividade.RAM_dataFinal and atividade.RAM_dataInicial
        )
        formatted_total_duracao = formatar_duracao(total_segundos)
        data.append({
            'Colaborador': '',
            'Cliente': '',
            'Serviço': '',
            'Atividade': '',
            'Data Inicial': '',
            'Data Final': 'Total de Duração:',
            'Duração': formatted_total_duracao
        })

        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer

@login_required(login_url="login/")
def gerar_relatorio(request):

    setores_usuario = request.user.groups.all()

    # Filtra as atividades de acordo com os setores associados ao cliente
    atividades = RegistroAtividadeModel.objects.filter(RAM_cliente__setor__in=setores_usuario).distinct()
    servicos = Servico.objects.filter(setor__in=setores_usuario).distinct()
    clientes = Cliente.objects.filter(setor__in=setores_usuario).distinct()
    atividades_filtro = Atividade.objects.filter(setor__in=setores_usuario).distinct()
    usuarios = User.objects.filter(groups__in=request.user.groups.all()).distinct()

    # Filtros opcionais por data
    hora = request.GET.get('hora')
    data_fim = request.GET.get('data_fim')
    if hora and data_fim:
        try:
            hora_datetime = datetime.strptime(hora, '%Y-%m-%d')
            data_fim_datetime = datetime.strptime(data_fim, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            atividades = atividades.filter(RAM_dataInicial__gte=hora_datetime, RAM_dataFinal__lte=data_fim_datetime)
        except ValueError:
            pass

    atividades = atividades.order_by('-RAM_dataInicial')
    paginator = Paginator(atividades, 20)
    atividades_page = paginator.get_page(request.GET.get('page'))

    # Calcula o total de segundos das atividades finalizadas
    total_segundos = sum(
        (a.RAM_dataFinal - a.RAM_dataInicial).total_seconds()
        for a in atividades if a.RAM_dataFinal and a.RAM_dataInicial
    )
    formatted_total_duracao = formatar_duracao(total_segundos)

    # Verifica se o usuário solicitou PDF ou Excel
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

    context = {
        'atividades': atividades_page,
        'page_obj': atividades_page,
        'clientes': clientes,
        'servicos': servicos,
        'atividades_filtro': atividades_filtro,
        'hora': hora,
        'data_fim': data_fim,
        'total_duracao': formatted_total_duracao,
        'is_admin': request.user.groups.filter(name='ADMINISTRADOR').exists(),
        'usuarios': usuarios,
    }
    return render(request, 'admin/relatorio.html', context)
