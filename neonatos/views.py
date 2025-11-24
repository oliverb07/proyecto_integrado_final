from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, DeleteView, TemplateView
)
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from gestion_roles.utils import registrar_accion
from django.contrib.auth.decorators import login_required
from gestion_roles.decorators import matrona_required
from django.utils.decorators import method_decorator

from .models import Madre, Parto, RecienNacido
from .forms import MadreForm, PartoForm, RecienNacidoForm
from .validators import _normalize_rut_basic
from .utils import format_rut_with_dots

@method_decorator([login_required, matrona_required], name='dispatch')
class HomeView(TemplateView):
    template_name = "neonatos/home.html"

@method_decorator([login_required, matrona_required], name='dispatch')
class MadreListView(ListView):
    model = Madre
    template_name = "neonatos/madre_list.html"
    context_object_name = "madres"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        madres = Madre.objects.prefetch_related("partos__recien_nacidos").order_by("-id")
        if q:
            try:
                norm = _normalize_rut_basic(q)
                madres = madres.filter(rut__iexact=norm)

                 # --- Registro de acción ---
                try:
                    if madres.exists():
                        registrar_accion(
                            self.request,
                            "Búsqueda por RUT",
                            f"Usuario {self.request.user.nombre} buscó el RUT '{q}' y obtuvo resultados."
                        )
                    else:
                        registrar_accion(
                            self.request,
                            "Búsqueda sin resultados",
                            f"Usuario {self.request.user.nombre} buscó el RUT '{q}' sin coincidencias."
                        )
                except Exception as e:
                    print("⚠️ Error registrando acción en bitácora:", e)
            except Exception:
                pass
        return madres
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx
    
@method_decorator([login_required, matrona_required], name='dispatch')
class MadreDetailView(DetailView):
    model = Madre
    template_name = "neonatos/madre_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        madre = self.object

        # Obtener partos asociados ordenados
        context["partos"] = madre.partos.all().order_by("-id")

        # Obtener recién nacidos de todos los partos de esta madre, ordenados
        context["recien_nacidos"] = (
            RecienNacido.objects.filter(parto__madre=madre).order_by("-id")
        )

        return context

@method_decorator([login_required, matrona_required], name='dispatch')
class MadreCreateView(CreateView):
    model = Madre
    form_class = MadreForm
    template_name = "neonatos/madre_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        madre = self.object
        registrar_accion(self.request, "Registro de madre", f"Madre {self.object.rut} creada")
        # redirigir a crear Parto encadenado
        return redirect(f"{reverse('neonatos:parto_create')}?madre_id={madre.pk}")

    def get_success_url(self):
        # no se usa por el redirect inmediato
        return reverse_lazy("neonatos:madre_detail", args=[self.object.pk])
    
@method_decorator([login_required, matrona_required], name='dispatch')
class MadreUpdateView(UpdateView):
    model = Madre
    form_class = MadreForm
    template_name = "neonatos/madre_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_accion(self.request, "Edición de madre", f"Madre {self.object.rut} actualizada")
        return response

    def get_success_url(self):
        # Volver a la lista moderna en lugar del detalle antiguo
        return reverse_lazy("neonatos:madre_list")
    
@method_decorator([login_required, matrona_required], name='dispatch')
class MadreDeleteView(DeleteView):
    model = Madre
    template_name = "neonatos/madre_confirm_delete.html"
    success_url = reverse_lazy("neonatos:madre_list")

    def post(self, request, *args, **kwargs):
        madre = self.get_object()
        registrar_accion(request, "Eliminación de madre", f"Se eliminó madre {madre.rut}")
        return super().delete(request, *args, **kwargs)
    
@method_decorator([login_required, matrona_required], name='dispatch')
class PartoCreateView(CreateView):
    model = Parto
    form_class = PartoForm
    template_name = "neonatos/parto_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # se pasa al form
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        madre_id = self.request.GET.get("madre_id")
        if madre_id:
            initial["madre"] = get_object_or_404(Madre, pk=madre_id)
        return initial

    def form_valid(self, form):
        madre_id = self.request.GET.get("madre_id")
        if madre_id:
            form.instance.madre = get_object_or_404(Madre, pk=madre_id)

        #  asigna automáticamente la matrona logueada
        if self.request.user.is_authenticated:
            form.instance.registrado_por = self.request.user

        response = super().form_valid(form)
        parto = self.object
        registrar_accion(self.request, "Registro de parto", f"Parto ID {self.object.id} de madre {self.object.madre.rut}")
        
        # redirigir a crear RN encadenado
        return redirect(f"{reverse('neonatos:rn_create')}?parto_id={parto.pk}")
        
        

    def get_success_url(self):
        return reverse_lazy("neonatos:madre_detail", args=[self.object.madre.pk])
    
@method_decorator([login_required, matrona_required], name='dispatch')   
# === PARTO: editar y eliminar ===
class PartoUpdateView(UpdateView):
    model = Parto
    form_class = PartoForm
    template_name = "neonatos/parto_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_accion(self.request, "Edición de parto", f"Parto ID {self.object.id} actualizado")
        return response

    def get_success_url(self):
        # Volver a la lista moderna
        return reverse_lazy("neonatos:madre_list")

@method_decorator([login_required, matrona_required], name='dispatch')
class PartoDeleteView(DeleteView):
    model = Parto
    template_name = "neonatos/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        parto = self.get_object()
        registrar_accion(request, "Eliminación de parto", f"Se eliminó parto ID {parto.id}")
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Evita que Django intente renderizar un template.
        Si se accede por GET (como cuando confirmas en SweetAlert),
        elimina directamente el objeto y redirige a la interfaz moderna.
        """
        self.object = self.get_object()
        self.object.delete()
        return redirect(reverse_lazy("neonatos:madre_list"))
    
@method_decorator([login_required, matrona_required], name='dispatch')   
class PartoDetailView(DetailView):
    model = Parto
    template_name = "neonatos/parto_detail.html"

@method_decorator([login_required, matrona_required], name='dispatch')
class BuscarPorRUTView(TemplateView):
    template_name = "neonatos/buscar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        ctx["query"] = q
        ctx["resultados"] = []
        if q:
            norm = _normalize_rut_basic(q)
            madre = Madre.objects.filter(rut__iexact=norm).first()
            if madre:
                ctx["resultados"] = [{
                    "id": madre.pk,
                    "rut": format_rut_with_dots(madre.rut),
                    "nombre": f"{madre.nombres} {madre.apellidos}",
                }]
                # Registrar la accion de busqueda
                try:
                    registrar_accion(
                    self.request,
                    "Búsqueda por RUT",
                    f"Usuario {self.request.user.nombre} buscó el RUT '{q}'"
                    )
                except Exception as e:
                    print("⚠️ Error registrando acción:", e)
            else:
                # Registrar también si no hubo resultados
                registrar_accion(
                    self.request,
                    "Búsqueda sin resultados",
                    f"Usuario {self.request.user.nombre} buscó el RUT '{q}' sin coincidencias"
                )
        return ctx


@method_decorator([login_required, matrona_required], name='dispatch')
# === RECIÉN NACIDO: editar y eliminar ===
class RNUpdateView(UpdateView):
    model = RecienNacido
    form_class = RecienNacidoForm
    template_name = "neonatos/rn_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_accion(
            self.request,
            "Edición de recién nacido",
            f"RN ID {self.object.id} del parto ID {self.object.parto.id} editado por {self.request.user}"
        )
        return response


    def get_success_url(self):
        # Volver a la lista moderna
        return reverse_lazy("neonatos:madre_list")
    
@method_decorator([login_required, matrona_required], name='dispatch')
class RNDeleteView(DeleteView):
    model = RecienNacido
    template_name = "neonatos/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        rn = self.get_object()
        registrar_accion(
            request,
            "Eliminación de recién nacido",
            f"RN ID {rn.id} del parto ID {rn.parto.id} eliminado por {request.user}"
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        # Volver al detalle de la madre tras eliminar
        return reverse_lazy("neonatos:madre_detail", args=[self.object.parto.madre.pk])

@method_decorator([login_required, matrona_required], name='dispatch')
class RecienNacidoDetailView(DetailView):
    model = RecienNacido
    template_name = "neonatos/rn_detail.html"

@method_decorator([login_required, matrona_required], name='dispatch') 
class RNCreateView(CreateView):
    model = RecienNacido
    form_class = RecienNacidoForm
    template_name = "neonatos/rn_form.html"

    def get_initial(self):
        initial = super().get_initial()
        parto_id = self.request.GET.get("parto_id")
        if parto_id:
            initial["parto"] = get_object_or_404(Parto, pk=parto_id)
        return initial

    def form_valid(self, form):
        parto_id = self.request.GET.get("parto_id")
        if not parto_id:
            form.add_error(None, "No se encontró el parto asociado para este recién nacido.")
            return self.form_invalid(form)

        parto = get_object_or_404(Parto, pk=parto_id)
        form.instance.parto = parto
        self.object = form.save()
        # Registrar la accion en bitacora
        registrar_accion(self.request, "Registro de recién nacido", f"RN ID {self.object.id} de madre {self.object.parto.madre.rut}")
        
        # En lugar de ir al detalle de madre, redirigimos al listado actualizado
        return redirect(reverse("neonatos:madre_list"))

    def get_success_url(self):
        return reverse("neonatos:madre_list")
    
@method_decorator([login_required, matrona_required], name='dispatch')  
# Pagina de confirmacion de eliminacion
class PartoDeleteView(DeleteView):
    model = Parto
    template_name = "neonatos/parto_confirm_delete.html"
    success_url = reverse_lazy("neonatos:madre_list")
