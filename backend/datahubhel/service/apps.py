from django.apps import AppConfig


class DataHubHelServiceConfig(AppConfig):
    name = 'datahubhel.service'
    label = 'datahubhel_service'
    verbose_name = 'DataHubHel Service'

    def ready(self):
        import datahubhel.service.signals.handlers  # noqa
