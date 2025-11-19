
def format_rut_with_dots(rut_norm: str) -> str:
    """Recibe '12345678-5' y devuelve '12.345.678-5'"""
    try:
        cuerpo, dv = rut_norm.split('-')
        cuerpo = cuerpo[::-1]
        partes = [cuerpo[i:i+3] for i in range(0, len(cuerpo), 3)]
        con_puntos = '.'.join(p[::-1] for p in partes)[::-1]
        return f"{con_puntos}-{dv}"
    except Exception:
        return rut_norm