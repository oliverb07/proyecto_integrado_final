from django.apps import AppConfig


class GestionRolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_roles'

    def ready(self):
        import gestion_roles.signals
