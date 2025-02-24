import datetime
from django.db import models
from django.contrib.auth.models import Group

# TABELA PERÍODO, CLIENTE, SERVIÇO E ATIVIDADE

class Periodo(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    setor = models.ManyToManyField(Group, related_name="cliente", blank=True)
    servicos = models.ManyToManyField('Servico', related_name='clientes', blank=True)

    def __str__(self):
        return self.nome
    
class Servico(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    setor = models.ManyToManyField(Group, related_name="servico", blank=True)
    atividades = models.ManyToManyField('Atividade', related_name='servicos', blank=True)

    def __str__(self):
        return self.nome

class Atividade(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    setor = models.ManyToManyField(Group, related_name="atividades", blank=True)

    def __str__(self):
        return self.nome