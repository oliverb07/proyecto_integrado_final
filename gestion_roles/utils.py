# gestion_roles/utils.py
from GeneradorReporte.models import Bitacora, Usuario

def registrar_accion(request, accion, detalle=""):
    """
    Registra una acción en la bitácora del sistema.
    """
    if request.user.is_authenticated:
        Bitacora.objects.create(
            usuario=request.user,  # 👈 usa el objeto, no el id
            accion=accion,
            detalle=detalle
        )
