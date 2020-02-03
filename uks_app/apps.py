from django.apps import AppConfig


class UksAppConfig(AppConfig):
    name = 'uks_app'

    def ready(self):
       import uks_app.signals 
