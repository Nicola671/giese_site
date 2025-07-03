from django.contrib import admin
from .models import Equipo, Noticia, Investigacion, Publicacion, BolsaTrabajo, Evento, Contacto

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesionalidad')
    search_fields = ('nombre', 'profesionalidad')

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha')
    search_fields = ('titulo',)
    list_filter = ('fecha',)

@admin.register(Investigacion)
class InvestigacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha')
    search_fields = ('titulo',)
    list_filter = ('fecha',)

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autores', 'fecha')
    search_fields = ('titulo', 'autores')
    list_filter = ('fecha',)

@admin.register(BolsaTrabajo)
class BolsaTrabajoAdmin(admin.ModelAdmin):
    list_display = ('puesto', 'empresa', 'fecha')
    search_fields = ('puesto', 'empresa')
    list_filter = ('fecha',)

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'fecha_cierre')
    search_fields = ('nombre',)
    list_filter = ('fecha', 'fecha_cierre')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'fecha', 'fecha_cierre', 'descripcion')
        }),
        ('Archivos', {
            'fields': ('pdf', 'archivo'),
            'description': 'Puedes subir un PDF y archivos adicionales para descargar.'
        }),
    )

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha')
    search_fields = ('nombre', 'email')
    list_filter = ('fecha',)
