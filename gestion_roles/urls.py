from django.urls import path
from gestion_roles import views

app_name = 'gestion_roles'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('verificar-otp/', views.verificar_otp, name='verificar_otp'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('registrar_parto/', views.registrar_parto, name='registrar_parto'),
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    
]