from django import forms
from .models import RegistroAtividadeModel

class RegistroAtividadeForm(forms.ModelForm):
    class Meta:
        model = RegistroAtividadeModel
        fields = ['RAM_cliente', 'RAM_servico', 'RAM_atividade', 'RAM_periodo']
