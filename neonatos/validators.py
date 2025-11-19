import re
from django.core.exceptions import ValidationError

def _normalize_rut_basic(value: str) -> str:
    """Normaliza un RUT a formato sin puntos y con guion (ej: 12345678-K)."""
    if not value:
        return value
    s = re.sub(r'[^0-9kK]', '', value)  # elimina puntos y espacios
    cuerpo, dv = s[:-1], s[-1].upper()
    return f"{cuerpo}-{dv}"

def _calc_dv(cuerpo: str) -> str:
    """Calcula el dígito verificador del cuerpo del RUT."""
    suma = 0
    mult = 2
    for d in reversed(cuerpo):
        suma += int(d) * mult
        mult += 1
        if mult > 7:
            mult = 2
    resto = 11 - (suma % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)

def rut_chile_validator(value: str):
    """
    Valida RUT chileno con máximo 8 dígitos antes del guion,
    y dígito verificador numérico o K.
    Acepta formatos con puntos o sin puntos.
    """
    if not value:
        raise ValidationError("Debe ingresar un RUT.")

    v = value.strip().replace('.', '').upper()

    if '-' not in v:
        raise ValidationError("El RUT debe incluir guion (ej: 12.345.678-5).")

    cuerpo, dv = v.split('-')

    # Validar cuerpo
    if not cuerpo.isdigit():
        raise ValidationError("El cuerpo del RUT debe ser numérico.")
    if len(cuerpo) > 8:
        raise ValidationError("El RUT no puede tener más de 8 dígitos antes del guion.")
    if dv not in "0123456789K":
        raise ValidationError("El dígito verificador debe ser un número o K.")

    # Validar dígito verificador
    if _calc_dv(cuerpo) != dv:
        raise ValidationError("Dígito verificador inválido.")

    # Retorna RUT limpio, normalizado (sin puntos)
    return f"{cuerpo}-{dv}"
