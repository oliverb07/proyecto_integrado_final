from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import rut_chile_validator
from decimal import Decimal

# === MODELOS ===

class Madre(models.Model):
    
    id = models.AutoField(primary_key=True, db_column="id_madre")
    rut = models.CharField("RUT", max_length=12, unique=True, validators=[rut_chile_validator],
                           help_text="RUT con guion y DV (ej: 12.345.678-5)")
    nombres = models.CharField("Nombres", max_length=100, help_text="Solo letras y espacios.")
    apellidos = models.CharField("Apellidos", max_length=100, help_text="Solo letras y espacios.")
    telefono = models.CharField("Teléfono", max_length=20, blank=True, help_text="Opcional")
    direccion = models.CharField("Dirección", max_length=200, blank=True)
    comuna = models.CharField("Comuna", max_length=100, blank=True)
    edad = models.PositiveIntegerField("Edad", validators=[MinValueValidator(10), MaxValueValidator(60)],
                                       help_text="Años cumplidos.")
    nacionalidad = models.CharField("Nacionalidad", max_length=50)
    pueblo_originario = models.CharField("Pertenece a pueblo originario", max_length=50)
    discapacidad = models.CharField("Discapacidad con credencial SENADIS", max_length=50)
    privada_libertad = models.CharField("Privada de libertad", max_length=50)
    controles_prenatales = models.CharField("Controles prenatales", max_length=50)

    paridad = models.CharField(
        max_length=20,
        choices=[
            ("nulipara", "Nulípara"),
            ("multipara", "Multípara"),
        ],
        default="nulipara"
    )

    cesareas_previas = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Madre"
        verbose_name_plural = "Madres"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rut})"


class Parto(models.Model):
    madre = models.ForeignKey(Madre, on_delete=models.CASCADE, related_name="partos")
    fecha_parto = models.DateField("Fecha del parto")
    # ⬇️ NUEVO, requerido para APS
    hora_parto = models.TimeField("Hora del parto", null=True, blank=True)

    TIPO_PARTO = [
        ("vaginal", "Vaginal"),
        ("instrumental", "Instrumental"),
        ("cesarea_electiva", "Cesárea electiva"),
        ("cesarea_urgencia", "Cesárea de urgencia"),
        ("domicilio", "Parto en domicilio"),
        ("prehospitalario", "Prehospitalario"),
    ]
    tipo_parto = models.CharField("Tipo de parto", max_length=20, choices=TIPO_PARTO)

    # ⬇️ **Campo necesario para Robson, REM y APS**
    TIPO_ATENCION = [
        ("programada", "Programada"),
        ("urgencia", "Urgencia"),
    ]
    tipo_atencion = models.CharField(
        "Tipo de atención",
        max_length=20,
        choices=TIPO_ATENCION,
        default="programada"
    )

    INICIO_PARTO = [("espontaneo", "Espontáneo"), ("inducido", "Inducido")]
    inicio_parto = models.CharField("Inicio de parto", max_length=12, choices=INICIO_PARTO, blank=True)

    ANALGESIA = [
        ("neuroaxial", "Neuroaxial"),
        ("endovenosa", "Endovenosa"),
        ("oxido_nitroso", "Óxido nitroso"),
        ("general", "General"),
        ("local", "Local"),
        ("no_farmacologica", "No farmacológica"),
    ]
    analgesia = models.CharField("Analgesia", max_length=20, choices=ANALGESIA, blank=True)

    ACOMP = [
        ("ninguno", "Ninguno"),
        ("trabajo_parto", "Trabajo de parto"),
        ("expulsivo", "Expulsivo"),
    ]
    acompanamiento = models.CharField("Acompañamiento", max_length=20, choices=ACOMP, blank=True)

    episiotomia = models.BooleanField("Episiotomía", default=False)
    oxitocina = models.BooleanField("Oxitocina profiláctica", default=False)
    plan_parto = models.BooleanField("Plan de parto registrado", default=False)
    contacto_piel_piel = models.BooleanField("Contacto piel con piel", default=False)
    alojamiento_conjunto = models.BooleanField("Alojamiento conjunto", default=False)
    cesarea_programada = models.BooleanField("Cesárea programada", default=False)

    edad_gestacional = models.PositiveIntegerField("Edad gestacional (semanas)",
                                                   validators=[MinValueValidator(20), MaxValueValidator(45)],
                                                   null=True, blank=True)
    
   
    
    complicaciones = models.BooleanField("Complicaciones", default=False)
    observaciones = models.TextField("Observaciones", blank=True)

    # ⬇️ NUEVOS CAMPOS PARA ROBSON
    PRESENTACION = [
        ("cefalica", "Cefálica"),
        ("pelvica", "Pélvica"),
        ("transversa", "Transversa"),
    ]
    presentacion_fetal = models.CharField("Presentación fetal", max_length=20, choices=PRESENTACION, null=True, blank=True)

    embarazo_multiple = models.BooleanField("Embarazo múltiple", default=False)

    # Usuario responsable
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, blank=True, verbose_name="Matrona responsable")

    class Meta:
        verbose_name = "Parto"
        verbose_name_plural = "Partos"

    def __str__(self):
        return f"Parto de {self.madre} {self.fecha_parto}"


class RecienNacido(models.Model):
    parto = models.ForeignKey("Parto", on_delete=models.CASCADE, related_name="recien_nacidos")
    sexo = models.CharField("Sexo", max_length=1, choices=[("F", "Femenino"), ("M", "Masculino")])
    peso = models.DecimalField(
        "Peso del recién nacido (kg)",
        max_digits=4,           # 1 antes del punto + 3 después
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal('0.000')),
            MaxValueValidator(Decimal('9.999')),
        ],
        null=True,
        blank=True,
        help_text="Formato: D o D.ddd (ej: 3.256). Máximo 9.999"
    )
    talla = models.PositiveIntegerField("Talla (cm)")
    apgar_1 = models.IntegerField("Puntuación Apgar (1 min)", null=True, blank=True)
    apgar_5 = models.IntegerField("Puntuación Apgar (5 min)", null=True, blank=True)
    anomalias_congenitas = models.BooleanField("Anomalías congénitas", default=False)
    profilaxis_hepatitisb = models.BooleanField("Profilaxis Hepatitis B", default=False)
    profilaxis_ocular = models.BooleanField("Profilaxis ocular", default=False)
    REANIMACION_CHOICES = [
        ("ninguna", "Ninguna"),
        ("basica", "Básica"),
        ("avanzada", "Avanzada"),
    ]
    reanimacion = models.CharField(
        "Reanimación",
        max_length=10,
        choices=REANIMACION_CHOICES,
        default="ninguna",
    )
    
    asfixia_neonatal = models.BooleanField("Asfixia neonatal", default=False)
    tamizaje_metabolico = models.BooleanField("Tamizaje metabólico", default=False)
    tamizaje_auditivo = models.BooleanField("Tamizaje auditivo", default=False)
    tamizaje_cardiaco = models.BooleanField("Tamizaje cardíaco", default=False)
    fallecido = models.BooleanField("Fallecido", default=False)
    
    TIPO_FALLECIMIENTO_CHOICES = [
        ("aborto", "Aborto"),
        ("mortinato", "Mortinato"),
        ("mortineonato", "Mortineonato"),
    ]
    tipo_fallecimiento = models.CharField(
        "Tipo de fallecimiento",
        max_length=20,
        choices=TIPO_FALLECIMIENTO_CHOICES,
        null=True,
        blank=True,
    )
    
    METODO_ALIMENTACION_CHOICES = [
        ("LME", "LME (Lactancia Materna Exclusiva)"),
        ("mixta", "Mixta"),
        ("formula", "Fórmula"),
        ("no_amamantado", "No amamantado"),
        ("HTLV_VIH", "HTLV/VIH"),
        ("Ley21155", "Ley 21.155"),
    ]
    metodo_alimentacion = models.CharField(
        "Método de alimentación",
        max_length=20,
        choices=METODO_ALIMENTACION_CHOICES,
        null=True,
        blank=True,
    )
    

    class Meta:
        verbose_name = "Recién nacido"
        verbose_name_plural = "Recién nacidos"

    def __str__(self):
        return f"RN de {self.parto.madre}"