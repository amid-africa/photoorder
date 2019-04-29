from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'products'

    """ Register our signals """
    def ready(self):
        import products.signals
