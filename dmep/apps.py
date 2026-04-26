from django.apps import AppConfig


class DmepConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dmep'

    def ready(self):
        import dmep.signals
