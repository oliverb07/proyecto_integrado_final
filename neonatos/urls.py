from django.urls import path
from .views import (
    HomeView, BuscarPorRUTView,
    MadreListView, MadreDetailView, MadreCreateView, MadreUpdateView, MadreDeleteView,
    PartoCreateView, PartoDetailView, PartoUpdateView, PartoDeleteView,
    RNCreateView, RecienNacidoDetailView, RNUpdateView, RNDeleteView,
    BuscarPorRUTView, HomeView
)

app_name = "neonatos"

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("madres/", MadreListView.as_view(), name="madre_list"),
    path("madre/nuevo/", MadreCreateView.as_view(), name="madre_create"),
    path("madre/<int:pk>/", MadreDetailView.as_view(), name="madre_detail"),
    path("madre/<int:pk>/editar/", MadreUpdateView.as_view(), name="madre_update"),
    path("madre/<int:pk>/eliminar/", MadreDeleteView.as_view(), name="madre_delete"),
    
    path("parto/<int:pk>/", PartoDetailView.as_view(), name="parto_detail"),
    path("rn/<int:pk>/", RecienNacidoDetailView.as_view(), name="rn_detail"),
    
    path("parto/nuevo/", PartoCreateView.as_view(), name="parto_create"),
    path("rn/nuevo/", RNCreateView.as_view(), name="rn_create"),
    path("buscar/", BuscarPorRUTView.as_view(), name="buscar_rut"),
    
    # Partos
    path("parto/<int:pk>/editar/", PartoUpdateView.as_view(), name="parto_update"),
    path("parto/<int:pk>/eliminar/", PartoDeleteView.as_view(), name="parto_delete"),

    # Recién nacidos
    path("rn/<int:pk>/editar/", RNUpdateView.as_view(), name="rn_update"),
    path("rn/<int:pk>/eliminar/", RNDeleteView.as_view(), name="rn_delete"),

]