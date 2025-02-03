from django.contrib import admin
from .models import Atividade, Cliente, Servico

class ClienteAdmin(admin.ModelAdmin):
    class Meta:
        model = Cliente
        fields = ('nome', 'setor', 'servicos')  # Assuming 'setor' is a ForeignKey or ManyToManyField

    list_display = ('id', 'nome', 'get_setores')
    list_display_links = ('id', 'nome')  # You don't need to include get_setores here
    filter_horizontal = ('setor', 'servicos')  # Only works if 'setor' is a ManyToManyField
    search_fields = ('nome',)

    def get_setores(self, obj):
        # Verifica se 'setor' é um ManyToManyField
        if hasattr(obj, 'setor') and hasattr(obj.setor, 'all'):
            return ", ".join([grupo.name for grupo in obj.setor.all()])
        return obj.setor.name if obj.setor else ''  # Se 'setor' for uma ForeignKey
    get_setores.short_description = 'Setores'

class ServicoAdmin(admin.ModelAdmin):
    class Meta:
        model = Servico
        fields = ('nome', 'setor', 'atividades')

    list_display = ('nome', 'get_setores', 'get_atividades')
    filter_horizontal = ('setor', 'atividades')  # Only works if 'setor' and 'atividades' are ManyToManyFields
    search_fields = ('nome',)

    def get_setores(self, obj):
        if hasattr(obj, 'setor') and hasattr(obj.setor, 'all'):
            return ", ".join([grupo.name for grupo in obj.setor.all()])
        return obj.setor.name if obj.setor else ''  # Se 'setor' for uma ForeignKey
    get_setores.short_description = 'Setores'

    def get_atividades(self, obj):
        # Supondo que 'atividades' seja um ManyToManyField
        return ", ".join([atividade.nome for atividade in obj.atividades.all()])
    get_atividades.short_description = 'Atividades'


class AtividadeAdmin(admin.ModelAdmin):
    class Meta:
        model = Atividade
        fields = ('nome', 'setor')

    list_display = ('nome', 'get_setores')
    filter_horizontal = ('setor',)
    search_fields = ('nome',)

    def get_setores(self, obj):
        if hasattr(obj, 'setor') and hasattr(obj.setor, 'all'):
            return ", ".join([grupo.name for grupo in obj.setor.all()])
        return obj.setor.name if obj.setor else ''  # Se 'setor' for uma ForeignKey
    get_setores.short_description = 'Setores'


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Servico, ServicoAdmin)
admin.site.register(Atividade, AtividadeAdmin)
