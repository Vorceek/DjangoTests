from django.contrib import admin
from .models import RegistroAtividadeModel
from django.utils.timezone import localtime

# REGISTRO ATIVIDADE
class RegistroAtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'RAM_cliente', 'RAM_servico', 'RAM_atividade', 'hora_formatada', 'RAM_dataFinal', 'RAM_duracao')
    list_display_links = ('id', 'RAM_cliente', 'RAM_servico')
    fields = ['RAM_cliente', 'RAM_servico', 'RAM_atividade']
    list_filter = ('RAM_cliente', 'RAM_servico', 'RAM_atividade', 'RAM_dataInicial')

    def hora_formatada(self, obj):
        return localtime(obj.RAM_dataInicial).strftime('%d/%m/%Y %H:%M')
    
    hora_formatada.short_description = 'Hora'

admin.site.register(RegistroAtividadeModel, RegistroAtividadeAdmin)
