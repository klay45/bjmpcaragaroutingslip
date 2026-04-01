from django.apps import AppConfig


class WebidConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webid'

    def ready(self):
        from . import signals
