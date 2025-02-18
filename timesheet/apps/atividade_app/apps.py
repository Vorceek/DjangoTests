from django.apps import AppConfig


class AtividadeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.atividade_app'

    #def ready(self):
    #    from .finalizador import start_scheduler
    #    start_scheduler()
