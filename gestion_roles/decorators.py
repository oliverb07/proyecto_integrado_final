from django.shortcuts import redirect
from django.contrib import messages

def matrona_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'Matrona':
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper

def supervisor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'Supervisor':
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper

def administrador_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'Administrador':
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper
