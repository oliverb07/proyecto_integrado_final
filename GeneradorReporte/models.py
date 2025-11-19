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
# TABLA: MADRE
# ===========================
class Madre(models.Model):
    id_madre = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12)
    nombre_completo = models.CharField(max_length=100)
    edad = models.IntegerField()
    nacionalidad = models.CharField(max_length=50)
    pueblo_originario = models.BooleanField()
    discapacidad = models.BooleanField()
    privada_libertad = models.BooleanField()
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono_contacto = models.CharField(max_length=15, blank=True, null=True)
    controles_prenatales = models.BooleanField()

    class Meta:
        db_table = 'madre'

    def __str__(self):
        return self.nombre_completo


# ===========================
# TABLA: PARTO
# ===========================
class Parto(models.Model):
    id_parto = models.AutoField(primary_key=True)
    id_madre = models.ForeignKey(Madre, on_delete=models.CASCADE, db_column='id_madre')
    fecha_parto = models.DateField()
    tipo_parto = models.CharField(max_length=50)
    inicio_parto = models.CharField(max_length=20, blank=True, null=True)
    analgesia = models.CharField(max_length=50, blank=True, null=True)
    acompanamiento = models.CharField(max_length=30, blank=True, null=True)
    episiotomia = models.BooleanField()
    oxitocina = models.BooleanField()
    plan_parto = models.BooleanField()
    contacto_piel_piel = models.BooleanField()
    alojamiento_conjunto = models.BooleanField()
    cesarea_programada = models.BooleanField()
    edad_gestacional = models.IntegerField()
    complicaciones = models.BooleanField()
    observaciones = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='registrado_por')

    class Meta:
        db_table = 'parto'

    def __str__(self):
        return f"Parto #{self.id_parto} - {self.id_madre.nombre_completo}"


# ===========================
# TABLA: COMPLICACION
# ===========================
class Complicacion(models.Model):
    id_complicacion = models.AutoField(primary_key=True)
    id_parto = models.ForeignKey(Parto, on_delete=models.CASCADE, db_column='id_parto')
    hemorragia_postparto = models.BooleanField()
    preeclampsia_eclampsia = models.BooleanField()
    sepsis = models.BooleanField()
    otras_complicaciones = models.TextField(blank=True, null=True)
    transfusion_sanguinea = models.BooleanField()
    histerectomia = models.BooleanField()
    traslado_uci = models.BooleanField()

    class Meta:
        db_table = 'complicacion'


# ===========================
# TABLA: RECIEN NACIDO
# ===========================
class RecienNacido(models.Model):
    id_rn = models.AutoField(primary_key=True)
    id_parto = models.ForeignKey(Parto, on_delete=models.CASCADE, db_column='id_parto')
    sexo = models.CharField(max_length=15)
    peso_nacer = models.DecimalField(max_digits=5, decimal_places=1)
    apgar_1 = models.IntegerField()
    apgar_5 = models.IntegerField()
    anomalias_congenitas = models.BooleanField()
    profilaxis_hepatitisb = models.BooleanField()
    profilaxis_ocular = models.BooleanField()
    reanimacion = models.CharField(max_length=20)
    asfixia_neonatal = models.BooleanField()
    tamizaje_metabolico = models.BooleanField()
    tamizaje_auditivo = models.BooleanField()
    tamizaje_cardiaco = models.BooleanField()
    fallecido = models.BooleanField()
    tipo_fallecimiento = models.CharField(max_length=20, blank=True, null=True)
    metodo_alimentacion = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'recien_nacido'


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

