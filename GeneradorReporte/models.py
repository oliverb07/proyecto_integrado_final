from django.db import models
from django.conf import settings

# ===========================
# TABLA: ROL
# ===========================
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'rol'

    def __str__(self):
        return self.nombre_rol


# ===========================
# TABLA: USUARIO
# ===========================
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    id_rol = models.ForeignKey(Rol, on_delete=models.DO_NOTHING, db_column='id_rol')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.usuario

# ===========================
# TABLA: BITACORA
# ===========================
class Bitacora(models.Model):
    id_evento = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        db_column='id_usuario'
    )
    accion = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'bitacora'
        verbose_name = "Registro de bitácora"
        verbose_name_plural = "Bitácora de sistema"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"

