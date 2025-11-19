from .models import Bitacora

def registrar_evento(usuario, accion, detalle=""):
    """Registrar manualmente un evento en la bitácora."""
    if usuario and usuario.is_authenticated:
        Bitacora.objects.create(
            id_usuario=usuario,
            accion=accion,
            detalle=detalle
        )
