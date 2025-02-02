from django.db import models
from django.conf import settings

from datetime import datetime
from zoneinfo import ZoneInfo

from apps.base_app.models import Atividade, Cliente, Servico

def hora_atual():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

class RegistroAtividadeModel(models.Model):
    ram_ativo = models.BooleanField(default=True)
    ram_colaborador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    ram_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    ram_servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    ram_atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    ram_dataInicial = models.DateTimeField(default=hora_atual, editable=False)
    ram_dataFinal = models.DateTimeField(null=True, blank=True)
    ram_duracao = models.DurationField(null=True, blank=True)


