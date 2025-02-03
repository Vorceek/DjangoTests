from django.contrib import admin
from .models import RegistroAtividadeModel
from django.utils.timezone import localtime

# REGISTRO ATIVIDADE
class RegistroAtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ram_cliente', 'ram_servico', 'ram_atividade', 'hora_formatada', 'ram_dataFinal', 'ram_duracao')
    list_display_links = ('id', 'ram_cliente', 'ram_servico')
    fields = ['ram_cliente', 'ram_servico', 'ram_atividade']
    list_filter = ('ram_cliente', 'ram_servico', 'ram_atividade', 'ram_dataInicial')

    def hora_formatada(self, obj):
        return localtime(obj.ram_dataInicial).strftime('%d/%m/%Y %H:%M')
    
    hora_formatada.short_description = 'Hora'

admin.site.register(RegistroAtividadeModel, RegistroAtividadeAdmin)
