from django.db import models
from django.conf import settings

from datetime import datetime
from zoneinfo import ZoneInfo

from apps.base_app.models import Atividade, Cliente, Servico

def hora_atual():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

class RegistroAtividadeModel(models.Model):
    RAM_ativo = models.BooleanField(default=True)
    RAM_colaborador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    RAM_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    RAM_servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    RAM_atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    RAM_dataInicial = models.DateTimeField(default=hora_atual, editable=False)
    RAM_dataFinal = models.DateTimeField(null=True, blank=True)
    RAM_duracao = models.DurationField(null=True, blank=True)

    @property
    def duracao_formatada(self):
        if self.RAM_duracao:
            total_segundos = self.RAM_duracao.total_seconds()
            horas = int(total_segundos // 3600)
            minutos = int((total_segundos % 3600) // 60)
            segundos = int(total_segundos % 60)
            return f"{horas}:{minutos:02d}:{segundos:02d}"
        return "0"



