from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'

    """ Register our signals """
    def ready(self):
        import user.signals
