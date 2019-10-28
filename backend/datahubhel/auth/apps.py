from django.apps import AppConfig


class DataHubHelAuthConfig(AppConfig):
    name = 'datahubhel.auth'
    label = 'datahubhel_auth'
    verbose_name = 'DataHubHel authentication and authorization'

    def ready(self):
        from .signals import handlers  # noqa
