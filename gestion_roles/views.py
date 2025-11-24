from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib import messages
from gestion_roles.decorators import matrona_required, supervisor_required, administrador_required
from gestion_roles.forms import UsuarioForm  # formulario para Usuario
from GeneradorReporte.models import Bitacora
import random
from django.core.mail import send_mail
from django.conf import settings

Usuario = get_user_model()

# ===========================
# VISTAS GENERALES
# ===========================

def inicio(request):
    # Vista de inicio general.
    return render(request, 'base.html')


def login_view(request):
    # Limpiar mensajes antiguos antes de mostrar el login
    storage = messages.get_messages(request)
    for _ in storage:
        pass

    # Login con redirección según rol.
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            otp = random.randint(100000, 999999)

            #Guardar datos temporales
            request.session['pending_user_id'] = user.id
            request.session['otp_code'] = otp

            # Mostrar OTP directamente en la pantalla (para Render)
            messages.success(request, f"Tu código OTP es: {otp}")

            return redirect('gestion_roles:verificar_otp') 
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, 'gestion_roles/login.html')


def verificar_otp(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('otp')
        codigo_real = str(request.session.get('otp_code'))
        user_id = request.session.get('pending_user_id')

        if codigo_ingresado == codigo_real:
            User = get_user_model()
            user = User.objects.get(id=user_id)

            #Limpiar variables temporales
            del request.session['otp_code']
            del request.session['pending_user_id']

            login(request, user)

            # Redirección según rol
            if user.rol == 'Matrona':
                return redirect('neonatos:home')
            elif user.rol == 'Supervisor':
                return redirect('GeneradorReporte:inicio')
            elif user.rol == 'Administrador':
                return redirect('gestion_roles:gestion_usuarios')
            
            return redirect('/') #fallback
        else:
            messages.error(request, "Codigo incorrecto. Intente nuevamente.")

    return render(request, 'gestion_roles/verificar_otp.html')
            

def cerrar_sesion(request):
    logout(request)
    return redirect('gestion_roles:login')


# ===========================
# VISTAS POR ROL
# ===========================

@login_required
@matrona_required
def registrar_parto(request):
    #Vista para que la matrona ingrese a neonatos.
    return render(request, 'neonatos/home.html')


@login_required
@supervisor_required
def reporte_rem_bs22(request):
    # Vista de reportes para supervisor.
    return render(request, 'GeneradorReporte/reportes.html')

@login_required
@supervisor_required
def reporte_rem_a09(request):
    # Vista de reportes para supervisor.
    return render(request, 'GeneradorReporte/reporte_a09.html')

@login_required
@supervisor_required
def reporte_rem_a04(request):
    # Vista de reportes para supervisor.
    return render(request, 'GeneradorReporte/reporte_a04.html')

@login_required
@supervisor_required
def ver_bitacora(request):
    logs = Bitacora.objects.select_related('id_usuario').order_by('-fecha_hora')
    return render(request, 'GeneradorReporte/bitacora.html', {'logs': logs})


@login_required
@administrador_required
def gestion_usuarios(request):
    # Vista principal de gestión de usuarios.
    usuarios = Usuario.objects.all()
    return render(request, 'gestion_roles/gestion_usuarios.html', {'usuarios': usuarios})


@login_required
@administrador_required
def crear_usuario(request):
    # Crear un nuevo usuario.
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('gestion_roles:gestion_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'gestion_roles/usuario_form.html', {'form': form})


@login_required
@administrador_required
def editar_usuario(request, id):
    # Editar usuario existente.
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('gestion_roles:gestion_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'gestion_roles/usuario_form.html', {'form': form})


@login_required
@administrador_required
def eliminar_usuario(request, id):
    # Eliminar un usuario.
    usuario = get_object_or_404(Usuario, id=id)
    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('gestion_roles:gestion_usuarios')
