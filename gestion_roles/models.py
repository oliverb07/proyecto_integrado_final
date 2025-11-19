from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
import uuid
# Create your models here.



class CodigoOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    creado = models.DateTimeField(default=timezone.now)
    valido_hasta = models.DateTimeField()
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.codigo} para {self.user.email}"


class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_rol
    
# ===========================
# TABLA: USUARIO
# ===========================

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nombre, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, nombre, password, **extra_fields)
    
class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (('Administrador', 'Administrador'), ('Supervisor', 'Supervisor'), ('Matrona', 'Matrona'))
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=50, choices=ROLES, default='Matrona')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre
    
class Madre(models.Model):
    rut = models.CharField(max_length=12)
    nombre_completo = models.CharField(max_length=100)
    edad = models.IntegerField()
    nacionalidad = models.CharField(max_length=50)
    pueblo_originario = models.BooleanField()
    discapacidad = models.BooleanField()
    privada_libertad = models.BooleanField()
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    controles_parentales = models.BooleanField()

    def __str__(self):
        return self.nombre_completo
    
class Parto(models.Model):
    madre = models.ForeignKey(Madre, on_delete=models.CASCADE)
    fecha_parto = models.DateField()
    tipo_parto = models.CharField(max_length=50)
    inicio_parto = models.CharField(max_length=20, blank=True, null=True)
    analgecia = models.CharField(max_length=50, blank=True, null=True)
    

    def __str__(self):
        return f"Parto de {self.madre.nombre_completo} el {self.fecha_parto}"
    