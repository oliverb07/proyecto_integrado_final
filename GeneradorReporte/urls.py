from django.urls import path
from . import views

app_name='GeneradorReporte'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('reportes/', views.vistaReportes, name='reportes'),
    path('rem-a09/', views.vistaReportea09, name='reporte_rem_a09'),
    path('rem-a04/', views.vistaReportea04, name='reporte_rem_a04'),
    path("exportar/reporte_bs22/", views.export_reporte_bs22, name="export_reporte_bs22"),
    path('exportar/rem_a09/', views.exportar_rem_a09, name='exportar_rem_a09'),
    path('exportar/rem_a04/', views.exportar_rem_a04, name='exportar_rem_a04'),
    path('bitacora/', views.verBitacora, name='ver_bitacora'),
    
]
