from django.contrib import admin
from .models import Madre, Parto, RecienNacido

@admin.register(Madre)
class MadreAdmin(admin.ModelAdmin):
    list_display = ("id","rut","nombres","apellidos","edad","nacionalidad","controles_prenatales")

@admin.register(Parto)
class PartoAdmin(admin.ModelAdmin):
    list_display = ("madre","fecha_parto","tipo_parto","inicio_parto","episiotomia","complicaciones")

@admin.register(RecienNacido)
class RNAdmin(admin.ModelAdmin):
    list_display = ("parto","sexo","peso","talla")