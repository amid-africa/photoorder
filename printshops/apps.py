from django.apps import AppConfig


class PrintshopsConfig(AppConfig):
    name = 'printshops'

    """ Register our signals """
    def ready(self):
        import printshops.signals
