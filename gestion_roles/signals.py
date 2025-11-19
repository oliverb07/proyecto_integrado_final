from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from GeneradorReporte.models import Bitacora

@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    Bitacora.objects.create(
        usuario=user,
        accion="Inicio de sesión",
        detalle=f"El usuario {user.nombre} ({user.email}) inició sesión."
    )

@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    if user:
        Bitacora.objects.create(
            usuario=user,
            accion="Cierre de sesión",
            detalle=f"El usuario {user.nombre} ({user.email}) cerró sesión."
        )
