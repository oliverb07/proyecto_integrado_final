from django import forms

from django.contrib.auth import get_user_model
from .models import Madre, Parto, RecienNacido
from .validators import _normalize_rut_basic, rut_chile_validator
import re
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone

def validar_solo_letras(value):
    patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s-]+$'
    if not re.match(patron, value):
        raise ValidationError("Solo se permiten letras (pueden incluir tildes y espacios).")


PESO_REGEX = re.compile(r'^[0-9](\.[0-9]{1,3})?$')

User = get_user_model()

class BaseBootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = field.help_text or field.label
            field.widget.attrs["title"] = field.help_text or field.label


class MadreForm(BaseBootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hacer todos los campos obligatorios y quitar textos de ayuda
        for field_name, field in self.fields.items():
            field.required = True
            field.help_text = None

        # --- Ajuste: mostrar solo los 8 dígitos al editar ---
        telefono_guardado = self.initial.get("telefono") or getattr(self.instance, "telefono", "")
        if telefono_guardado and telefono_guardado.startswith("+569"):
            # Mostrar solo los 8 dígitos después del prefijo +569
            self.initial["telefono"] = telefono_guardado.replace("+569", "")

        # Asignar ejemplos (placeholders) para cada campo del formulario
        placeholders = {
            "nombres": "Ej: María José",
            "apellidos": "Ej: González Soto",
            "telefono": "Ej: 12345678",  # <-- Ya no mostramos +569 aquí
            "domicilio": "Ej: Calle Los Álamos 123",
            "comuna": "Ej: Chillán",
            "edad": "Ej: 32",
            "nacionalidad": "Ej: Chilena",
            "direccion": "Ej: Pasaje Los Robles 45, Chillán",
        }

        for field_name, text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"placeholder": text})

    
    rut = forms.CharField(
        label="RUT",
        max_length=12,
        required=True,  # hace obligatorio el campo
        help_text="Ej: 12.345.678-5",
        widget=forms.TextInput(
            attrs={
                "placeholder": "12.345.678-5",
                "pattern": r"\d{1,2}\.?\d{3}\.?\d{3}-[0-9kK]",
                "title": "Formato válido: 12.345.678-5",
                "autocomplete": "off",  # evita autocompletar valores viejos
            }
        ),
    )
    
    telefono = forms.CharField(
        label="Teléfono",
        max_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "12345678",
                "pattern": r"\d{8}",
                "title": "Ingrese solo 8 dígitos (ej: 12345678)",
                "autocomplete": "off",
                "oninput": "this.value = this.value.replace(/[^0-9]/g, '').slice(0,8);",
                "style": "width: 100%;",
            }
        ),
        help_text=None,
    )
    
    #Campos que solo permiten letras
    nombres = forms.CharField(
        label="Nombres",
        validators=[validar_solo_letras],
        widget=forms.TextInput(attrs={"placeholder": "Ej: María José"})
    )

    apellidos = forms.CharField(
        label="Apellidos",
        validators=[validar_solo_letras],
        widget=forms.TextInput(attrs={"placeholder": "Ej: González Soto"})
    )

    comuna = forms.CharField(
        label="Comuna",
        validators=[validar_solo_letras],
        widget=forms.TextInput(attrs={"placeholder": "Ej: Chillán"})
    )

    NACIONALIDAD_CHOICES = [
    ("", "Seleccione nacionalidad..."),  
    ("chilena", "Chilena"),
    ("migrante", "Migrante"),
    ]
    nacionalidad = forms.ChoiceField(
        label="Nacionalidad",
        choices=NACIONALIDAD_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar una nacionalidad válida"},
    )
    
    PUEBLO_ORIGINARIO_CHOICES = [
        ("", "Seleccione una opción..."),
        ("si", "Sí"),
        ("no", "No"),
    ]
    pueblo_originario = forms.ChoiceField(
        label="Pertenece a pueblo originario",
        choices=PUEBLO_ORIGINARIO_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar si pertenece o no a un pueblo originario"},
    )
    
    DISCAPACIDAD_CHOICES = [
    ("", "Seleccione una opción..."),
    ("Si", "Sí"),
    ("No", "No"),
    ]

    discapacidad = forms.ChoiceField(
        label="Discapacidad con credencial SENADIS",
        choices=DISCAPACIDAD_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar si posee o no credencial de discapacidad SENADIS"},
    )
    
    PRIVADA_LIBERTAD_CHOICES = [
    ("", "Seleccione una opción..."),
    ("Si", "Sí"),
    ("No", "No"),
    ]

    privada_libertad = forms.ChoiceField(
        label="Privada de libertad",
        choices=PRIVADA_LIBERTAD_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar si la madre se encuentra o no privada de libertad"},
    )

    CONTROLES_PRENATALES_CHOICES = [
    ("", "Seleccione una opción..."),
    ("Si", "Sí"),
    ("No", "No"),
    ]

    controles_prenatales = forms.ChoiceField(
        label="Controles prenatales realizados",
        choices=CONTROLES_PRENATALES_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar si la madre realizó o no controles prenatales"},
    )

    def clean_controles_prenatales(self):
        controles = self.cleaned_data.get("controles_prenatales", "").strip()
        if not controles:
            raise forms.ValidationError("Debe seleccionar una opción válida.")
        return controles



    def clean_privada_libertad(self):
        privada_libertad = self.cleaned_data.get("privada_libertad", "").strip()
        if not privada_libertad:
            raise forms.ValidationError("Debe seleccionar una opción válida.")
        return privada_libertad


    def clean_discapacidad(self):
        discapacidad = self.cleaned_data.get("discapacidad", "").strip()
        if not discapacidad:
            raise forms.ValidationError("Debe seleccionar una opción válida.")
        return discapacidad

    def clean_pueblo_originario(self):
        valor = self.cleaned_data.get("pueblo_originario", "").strip()
        if not valor:
            raise forms.ValidationError("Debe seleccionar si pertenece o no a un pueblo originario.")
        return valor

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "").strip()
        if not telefono.isdigit() or len(telefono) != 8:
            raise forms.ValidationError("Debe ingresar exactamente 8 dígitos numéricos.")
        return f"+569{telefono}"
    
    def clean_nacionalidad(self):
        nacionalidad = self.cleaned_data.get("nacionalidad", "").strip()
        if not nacionalidad:
            raise forms.ValidationError("Debe seleccionar una nacionalidad válida.")
        return nacionalidad
    
    
    
    def clean_rut(self):
        rut = self.cleaned_data.get("rut", "").strip().upper()
        rut = rut.replace(".", "")
        rut_chile_validator(rut)
        return _normalize_rut_basic(rut)
    
    def clean_edad(self):
        edad = self.cleaned_data.get("edad")
        if edad is not None:
            if edad < 10 or edad > 60:
                raise ValidationError("La edad debe estar entre 10 y 60 años.")
        return edad
        
    """Valida coherencia entre edad y fecha de nacimiento"""    
    def clean(self):
        cleaned_data = super().clean()
        edad = cleaned_data.get("edad")
        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")

        if edad and fecha_nacimiento:
            hoy = date.today()
            edad_calculada = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
            )
            if abs(edad - edad_calculada) > 1:
                raise ValidationError(
                    "La edad no coincide con la fecha de nacimiento ingresada."
                )
        return cleaned_data
    
    def clean_paridad(self):
        paridad = self.cleaned_data.get("paridad")
        if paridad is None or paridad < 0:
            raise ValidationError("La paridad no puede ser negativa.")
        return paridad

    def clean_cesareas_previas(self):
        valor = self.cleaned_data.get("cesareas_previas")
        if valor is None or valor < 0:
            raise ValidationError("Las cesáreas previas no pueden ser negativas.")
        return valor

    class Meta:
        model = Madre
        fields = [
            "rut", "nombres", "apellidos",
            "telefono", "direccion", "comuna",
            "edad", "nacionalidad", "pueblo_originario",
            "discapacidad", "privada_libertad","controles_prenatales",
            "paridad", "cesareas_previas",
        ]
        widgets = {
            "pueblo_originario": forms.Select(choices=[(True, "Sí"), (False, "No")]),
            "discapacidad": forms.Select(choices=[(True, "Sí"), (False, "No")]),
            "privada_libertad": forms.Select(choices=[(True, "Sí"), (False, "No")]),
            "controles_prenatales": forms.Select(choices=[(True, "Sí"), (False, "No")]),
        }


class PartoForm(BaseBootstrapForm):
    def __init__(self, *args, **kwargs):
        # Recibir request desde la vista
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        
        # 🔹 Ocultar el campo madre
        if "madre" in self.fields:
            self.fields["madre"].widget = forms.HiddenInput()
            
        # 🔹 Formato de fecha
        if "fecha_parto" in self.fields:
            self.fields["fecha_parto"].input_formats = ["%Y-%m-%d"]
            
        # 🔹 Edad gestacional obligatoria
        if "edad_gestacional" in self.fields:
            self.fields["edad_gestacional"].required = True
            self.fields["edad_gestacional"].error_messages = {
                "required": "Debe ingresar la edad gestacional del parto."
            }

        # 🔹 Matrona responsable (registrado_por) — oculto
        if "registrado_por" in self.fields:
            self.fields["registrado_por"].widget = forms.HiddenInput()
        
        # Guardar nombre visible para mostrar en template
        self.matrona_nombre = None
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            nombre = getattr(user, "nombre", None)  # ✅ usa el campo real del modelo Usuario
            rol = getattr(user, "rol", None)        # opcional: muestra también el rol
            if nombre:
                # Muestra "Paola Araya (Matrona)"
                self.matrona_nombre = f"{nombre} ({rol})" if rol else nombre
            else:
                # Si por alguna razón no hay nombre, usa el correo
                self.matrona_nombre = getattr(user, "email", "Usuario desconocido")

            
    OPCIONES_SI_NO = [
    ("", "Seleccione una opción..."),
    ("Si", "Sí"),
    ("No", "No"),
    ]

    TIPO_PARTO_CHOICES = [
        ("", "Seleccione una opción..."),
        ("vaginal", "Vaginal"),
        ("instrumental", "Instrumental"),
        ("cesarea_electiva", "Cesárea electiva"),
        ("cesarea_urgencia", "Cesárea de urgencia"),
        ("domicilio", "Domicilio"),
        ("prehospitalario", "Prehospitalario"),
    ]

    INICIO_PARTO_CHOICES = [
        ("", "Seleccione una opción..."),
        ("espontaneo", "Espontáneo"),
        ("inducido", "Inducido"),
    ]

    ANALGESIA_CHOICES = [
        ("", "Seleccione una opción..."),
        ("neuroaxial", "Neuroaxial"),
        ("endovenosa", "Endovenosa"),
        ("oxido_nitroso", "Óxido nitroso"),
        ("general", "General"),
        ("local", "Local"),
        ("no_farmacologica", "No farmacológica"),
    ]

    ACOMPANAMIENTO_CHOICES = [
        ("", "Seleccione una opción..."),
        ("ninguno", "Ninguno"),
        ("trabajo_parto", "Durante el trabajo de parto"),
        ("expulsivo", "Durante el expulsivo"),
    ]

    tipo_parto = forms.ChoiceField(
        label="Tipo de parto",
        choices=TIPO_PARTO_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar el tipo de parto."},
    )

    inicio_parto = forms.ChoiceField(
        label="Inicio del parto",
        choices=INICIO_PARTO_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar cómo se inició el parto."},
    )

    analgesia = forms.ChoiceField(
        label="Analgesia utilizada",
        choices=ANALGESIA_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe seleccionar el tipo de analgesia utilizada."},
    )

    acompanamiento = forms.ChoiceField(
        label="Acompañamiento durante el parto",
        choices=ACOMPANAMIENTO_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe indicar si hubo acompañamiento y en qué etapa."},
    )

    hora_parto = forms.TimeField(
        label="Hora del parto",
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )

    tipo_atencion = forms.ChoiceField(
        label="Tipo de atención",
        choices=[("", "Seleccione..."), ("programada", "Programada"), ("urgencia", "Urgencia")],
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    presentacion_fetal = forms.ChoiceField(
        label="Presentación fetal",
        choices=[
            ("", "Seleccione..."),
            ("cefalica", "Cefálica"),
            ("pelvica", "Pélvica"),
            ("transversa", "Transversa"),
        ],
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    embarazo_multiple = forms.ChoiceField(
        label="Embarazo múltiple",
        choices=[("", "Seleccione..."), (True, "Sí"), (False, "No")],
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )



    class Meta:
        model = Parto
        fields = [
            "madre", "fecha_parto", "hora_parto", "tipo_parto", "tipo_atencion",
            "inicio_parto", "analgesia",
            "acompanamiento", "episiotomia", "oxitocina", "plan_parto",
            "contacto_piel_piel", "alojamiento_conjunto", "cesarea_programada",
            "presentacion_fetal", "embarazo_multiple",
            "edad_gestacional", "complicaciones", "observaciones", "registrado_por",
        ]
        widgets = {
        "observaciones": forms.Textarea(attrs={
            "rows": 3,
            "maxlength": 250,
            "placeholder": "Máximo 250 caracteres...",
            "style": "resize: none;",
        }),

        "episiotomia": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "oxitocina": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "plan_parto": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "contacto_piel_piel": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "alojamiento_conjunto": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "cesarea_programada": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "complicaciones": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),

        "fecha_parto": forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        "edad_gestacional": forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 39",
            "min": 20,
            "max": 45,
            "title": "Ingrese la edad gestacional en semanas",
        }),
    }

        
    def clean_tipo_parto(self):
        valor = self.cleaned_data.get("tipo_parto", "")
        if not valor:
            raise forms.ValidationError("Debe seleccionar el tipo de parto.")
        return valor

    def clean_inicio_parto(self):
        valor = self.cleaned_data.get("inicio_parto", "")
        if not valor:
            raise forms.ValidationError("Debe seleccionar cómo se inició el parto.")
        return valor

    def clean_analgesia(self):
        valor = self.cleaned_data.get("analgesia", "")
        if not valor:
            raise forms.ValidationError("Debe seleccionar el tipo de analgesia utilizada.")
        return valor

    def clean_acompanamiento(self):
        valor = self.cleaned_data.get("acompanamiento", "")
        if not valor:
            raise forms.ValidationError("Debe indicar si hubo acompañamiento durante el parto.")
        return valor
        
    def clean_episiotomia(self):
        valor = self.cleaned_data.get("episiotomia")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Episiotomía.")

    def clean_oxitocina(self):
        valor = self.cleaned_data.get("oxitocina")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Oxitocina profiláctica.")

    def clean_plan_parto(self):
        valor = self.cleaned_data.get("plan_parto")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Plan de parto registrado.")

    def clean_contacto_piel_piel(self):
        valor = self.cleaned_data.get("contacto_piel_piel")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Contacto piel con piel.")

    def clean_alojamiento_conjunto(self):
        valor = self.cleaned_data.get("alojamiento_conjunto")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Alojamiento conjunto.")

    def clean_cesarea_programada(self):
        valor = self.cleaned_data.get("cesarea_programada")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Cesárea programada.")

    def clean_complicaciones(self):
        valor = self.cleaned_data.get("complicaciones")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida para Complicaciones.")
    
    def clean_tipo_atencion(self):
        valor = self.cleaned_data.get("tipo_atencion")
        if not valor:
            raise forms.ValidationError("Debe seleccionar si fue programada o de urgencia.")
        return valor

    def clean_presentacion_fetal(self):
        valor = self.cleaned_data.get("presentacion_fetal")
        if not valor:
            raise forms.ValidationError("Debe seleccionar la presentación fetal.")
        return valor

    def clean_embarazo_multiple(self):
        valor = self.cleaned_data.get("embarazo_multiple")
        if valor in ["True", True]:
            return True
        if valor in ["False", False]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida.")

class RecienNacidoForm(BaseBootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        boolean_fields = [
            "anomalias_congenitas", "profilaxis_hepatitisb", "profilaxis_ocular",
            "asfixia_neonatal", "tamizaje_metabolico", "tamizaje_auditivo",
            "tamizaje_cardiaco", "fallecido",
        ]
        for field_name in boolean_fields:
            field = self.fields.get(field_name)
            if field and isinstance(field.widget, forms.Select):
                instance = getattr(self.instance, field_name, None)
                if instance is True:
                    field.initial = "True"
                elif instance is False:
                    field.initial = "False"

        # Aplica estilo Bootstrap a todos los selects
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"

    
    OPCIONES_SI_NO = [
        ("", "Seleccione una opción..."),
        (True, "Sí"),
        (False, "No"),
    ]

    REANIMACION_CHOICES = [
        ("", "Seleccione tipo de reanimación..."),
        ("ninguna", "Ninguna"),
        ("basica", "Básica"),
        ("avanzada", "Avanzada"),
    ]

    TIPO_FALLECIMIENTO_CHOICES = [
        ("", "Seleccione tipo de fallecimiento..."),
        ("aborto", "Aborto"),
        ("mortinato", "Mortinato"),
        ("mortineonato", "Mortineonato"),
    ]

    METODO_ALIMENTACION_CHOICES = [
        ("", "Seleccione método de alimentación..."),
        ("LME", "LME (Lactancia Materna Exclusiva)"),
        ("mixta", "Mixta"),
        ("formula", "Fórmula"),
        ("no_amamantado", "No amamantado"),
        ("HTLV_VIH", "HTLV/VIH"),
        ("Ley21155", "Ley 21.155"),
    ]
    
    SEXO_CHOICES = [
    ("", "Seleccione una opción..."),
    ("M", "Masculino"),
    ("F", "Femenino"),
    ]
    
    APGAR_CHOICES = [
    ("", "Seleccione una opción..."),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ]


    sexo = forms.ChoiceField(
        label="Sexo",
        choices=SEXO_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": "Debe seleccionar el sexo del recién nacido."
        },
    )

    apgar_1 = forms.ChoiceField(
        label="Puntuación Apgar (1 min)",
        choices=APGAR_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": "Debe seleccionar la puntuación Apgar al 1 minuto."
        },
    )

    apgar_5 = forms.ChoiceField(
        label="Puntuación Apgar (5 min)",
        choices=APGAR_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": "Debe seleccionar la puntuación Apgar a los 5 minutos."
        },
    )
    
    anomalias_congenitas = forms.TypedChoiceField(
        label="Anomalías congénitas",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    profilaxis_hepatitisb = forms.TypedChoiceField(
        label="Profilaxis Hepatitis B",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    profilaxis_ocular = forms.TypedChoiceField(
        label="Profilaxis ocular",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    asfixia_neonatal = forms.TypedChoiceField(
        label="Asfixia neonatal",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    tamizaje_metabolico = forms.TypedChoiceField(
        label="Tamizaje metabólico",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    tamizaje_auditivo = forms.TypedChoiceField(
        label="Tamizaje auditivo",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    tamizaje_cardiaco = forms.TypedChoiceField(
        label="Tamizaje cardíaco",
        choices=OPCIONES_SI_NO,
        coerce=lambda x: x == "True" or x is True,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    fallecido = forms.TypedChoiceField(
        label="Fallecido",
        choices=[
            ("", "Seleccione una opción..."),
            (True, "Sí"),
            (False, "No"),
        ],
        coerce=lambda x: x in [True, "True", "true"],
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Debe indicar si el recién nacido falleció."},
    )


    reanimacion = forms.ChoiceField(
        label="Tipo de reanimación",
        choices=REANIMACION_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    tipo_fallecimiento = forms.ChoiceField(
        label="Tipo de fallecimiento",
        choices=TIPO_FALLECIMIENTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    metodo_alimentacion = forms.ChoiceField(
        label="Método de alimentación",
        choices=METODO_ALIMENTACION_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": "Debe seleccionar el método de alimentación del recién nacido."
        },
    )
    
    class Meta:
        model = RecienNacido
        fields = ["parto", "sexo", "peso", "talla",
                  "apgar_1", "apgar_5",
                  "anomalias_congenitas",
                  "profilaxis_hepatitisb",
                  "profilaxis_ocular",
                  "reanimacion",
                  "asfixia_neonatal",
                  "tamizaje_metabolico",
                  "tamizaje_auditivo",
                  "tamizaje_cardiaco",
                  "fallecido",
                  "tipo_fallecimiento",
                  "metodo_alimentacion",]
        widgets = {
        "animalias_congenitas": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "profilaxis_hepatitisb": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "profilaxis_ocular": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "reanimacion": forms.Select(
            choices=[
                ("", "Seleccione una opción..."),
                ("ninguna", "Ninguna"),
                ("basica", "Básica"),
                ("avanzada", "Avanzada"),
            ],
            attrs={"class": "form-select", "required": "required"},
        ),
        "asfixia_neonatal": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "tamizaje_metabolico": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "tamizaje_auditivo": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
        "tamizaje_cardiaco": forms.Select(
            choices=[("", "Seleccione una opción..."), (True, "Sí"), (False, "No")],
            attrs={"class": "form-select", "required": "required"},
        ),
    }

    def clean_fecha_parto(self):
        fecha_parto = self.cleaned_data.get("fecha_parto")
        if not fecha_parto:
            raise forms.ValidationError("Debe ingresar una fecha válida para el parto.")
        return fecha_parto

    def clean_sexo(self):
        valor = self.cleaned_data.get("sexo", "").strip()
        if not valor:
            raise forms.ValidationError("Debe seleccionar el sexo del recién nacido.")
        return valor

    def clean_peso(self):
        peso = self.cleaned_data.get("peso")

        if peso in [None, ""]:
            raise forms.ValidationError("Debe ingresar el peso del recién nacido en kilogramos.")

        try:
            peso = float(peso)
        except ValueError:
            raise forms.ValidationError("El peso debe ser un número válido (use punto decimal).")

        # Validación de rango clínico (prematuros y macrosómicos)
        if peso < 0.5 or peso > 6.0:
            raise forms.ValidationError("El peso debe estar entre 0.5 kg y 6.0 kg.")

        return round(peso, 3)

    def _to_bool(self, valor):
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe seleccionar una opción válida.")

    def clean_animalias_congenitas(self):
        return self._to_bool(self.cleaned_data.get("animalias_congenitas"))

    def clean_profilaxis_hepatitisb(self):
        return self._to_bool(self.cleaned_data.get("profilaxis_hepatitisb"))

    def clean_profilaxis_ocular(self):
        return self._to_bool(self.cleaned_data.get("profilaxis_ocular"))

    def clean_asfixia_neonatal(self):
        return self._to_bool(self.cleaned_data.get("asfixia_neonatal"))

    def clean_tamizaje_metabolico(self):
        return self._to_bool(self.cleaned_data.get("tamizaje_metabolico"))

    def clean_tamizaje_auditivo(self):
        return self._to_bool(self.cleaned_data.get("tamizaje_auditivo"))

    def clean_tamizaje_cardiaco(self):
        return self._to_bool(self.cleaned_data.get("tamizaje_cardiaco"))

    def clean_fallecido(self):
        valor = self.cleaned_data.get("fallecido", "")
        if valor in [True, "True", "true"]:
            return True
        elif valor in [False, "False", "false"]:
            return False
        raise forms.ValidationError("Debe indicar si el recién nacido falleció.")

    
    

    
    def clean_talla(self):
        talla = self.cleaned_data.get("talla", "")

        # Si está vacío, no se valida (puede ser opcional)
        if talla in [None, ""]:
            return talla

        # Convierte a string y limpia espacios
        talla_str = str(talla).strip()

        # Expresión regular: hasta 2 dígitos, opcionalmente con un decimal (ej: 49 o 49.5)
        patron = r"^\d{1,2}(\.\d)?$"

        if not re.match(patron, talla_str):
            raise ValidationError("Ingrese una talla válida en cm (máximo 2 dígitos y 1 decimal).")

        try:
            talla_float = float(talla_str)
        except ValueError:
            raise ValidationError("La talla debe ser un número válido.")

        # Validación de rango clínico razonable
        if talla_float < 10 or talla_float > 99.9:
            raise ValidationError("La talla debe estar entre 10.0 cm y 99.9 cm.")

        return talla_float

    def clean_apgar_1(self):
        valor = self.cleaned_data.get("apgar_1", "")
        if not valor:
            raise forms.ValidationError("Debe seleccionar la puntuación Apgar al 1 minuto.")
        try:
            valor_int = int(valor)
        except ValueError:
            raise forms.ValidationError("La puntuación Apgar 1 debe ser un número entero.")
        if valor_int < 1 or valor_int > 5:
            raise forms.ValidationError("La puntuación Apgar 1 debe estar entre 1 y 5.")
        return valor_int


    def clean_apgar_5(self):
        valor = self.cleaned_data.get("apgar_5", "")
        if not valor:
            raise forms.ValidationError("Debe seleccionar la puntuación Apgar a los 5 minutos.")
        try:
            valor_int = int(valor)
        except ValueError:
            raise forms.ValidationError("La puntuación Apgar 5 debe ser un número entero.")
        if valor_int < 1 or valor_int > 5:
            raise forms.ValidationError("La puntuación Apgar 5 debe estar entre 1 y 5.")
        return valor_int


    def clean(self):
        cleaned_data = super().clean()
        fallecido = cleaned_data.get("fallecido")
        tipo_fallecimiento = cleaned_data.get("tipo_fallecimiento")

        # Si fallecido = True → tipo_fallecimiento obligatorio
        if fallecido is True:
            if not tipo_fallecimiento:
                self.add_error(
                    "tipo_fallecimiento",
                    "Debe seleccionar el tipo de fallecimiento si el recién nacido está marcado como fallecido.",
                )
        else:
            # Si no falleció → limpiar campo para evitar datos residuales
            cleaned_data["tipo_fallecimiento"] = None

        return cleaned_data