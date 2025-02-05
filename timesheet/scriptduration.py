from django.db.models import F, ExpressionWrapper, DurationField
from apps.atividade_app.models import RegistroAtividadeModel

RegistroAtividadeModel.objects.filter(
    RAM_dataFinal__isnull=False,
    RAM_duracao__isnull=True
).update(
    RAM_duracao=ExpressionWrapper(F('RAM_dataFinal') - F('RAM_dataInicial'), output_field=DurationField())
)
