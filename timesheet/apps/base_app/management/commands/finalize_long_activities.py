import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from apps.atividade_app.models import RegistroAtividadeModel

class Command(BaseCommand):
    help = "Finaliza as atividades abertas que passaram de 12 horas, verificando a cada 5 segundos."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a verificação contínua de atividades...")
        try:
            while True:
                cutoff = timezone.now() - timedelta(hours=12)
                atividades = RegistroAtividadeModel.objects.filter(RAM_dataFinal__isnull=True, RAM_dataInicial__lte=cutoff)
                count = 0
                if atividades.exists():
                    with transaction.atomic():
                        for atividade in atividades:
                            atividade.RAM_ativo = False
                            atividade.RAM_dataFinal = timezone.now()
                            atividade.RAM_duracao = atividade.RAM_dataFinal - atividade.RAM_dataInicial
                            atividade.save()
                            count += 1
                    if count:
                        self.stdout.write(f"Finalizadas {count} atividades.")
                time.sleep(5)
        except KeyboardInterrupt:
            self.stdout.write("Encerrando a verificação contínua.")