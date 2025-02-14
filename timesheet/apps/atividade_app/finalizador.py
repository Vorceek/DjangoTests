# myapp/scheduler.py
import logging
from datetime import timedelta
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from .models import RegistroAtividadeModel

logger = logging.getLogger(__name__)

def finalize_long_activities():
    cutoff = timezone.now() - timedelta(hours=11.5)
    activities = RegistroAtividadeModel.objects.filter(RAM_dataFinal__isnull=True, RAM_dataInicial__lte=cutoff)
    for activity in activities:
        activity.RAM_dataFinal = timezone.now()
        # Calcula a duração como a diferença entre a data final e a data inicial
        duration = activity.RAM_dataFinal - activity.RAM_dataInicial
        activity.RAM_duracao = duration
        activity.save()


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    scheduler.add_job(
        finalize_long_activities,
        trigger="interval",
        minutes=30,  # roda a cada 30 minutos
        id="finalize_long_activities",
        max_instances=1,
        replace_existing=True,
    )
    
    try:
        scheduler.start()
        logger.info("Scheduler iniciado!")
    except Exception as e:
        logger.error("Erro ao iniciar scheduler: %s", e)
