# Vistas para eventos, usuarios, etc. se definirán aquí
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Equipo, Noticia, Investigacion, Publicacion, PublicacionImagen, BolsaTrabajo, Evento
from .forms import EquipoForm, CustomLoginForm, NoticiaForm, InvestigacionForm, PublicacionForm
from django.db import models

def inicio(request):
    # Puedes personalizar el contenido de quienes somos aquí
    quienes_somos = "Somos GIESE, un grupo de investigación y extensión de la Universidad Nacional de Mar del Plata."
    return render(request, 'core/inicio.html', {'quienes_somos': quienes_somos})

def equipo(request):
    tipos = ['Director/a', 'Profesor/a', 'Preceptor/a']
    equipos_agrupados = {}
    q = request.GET.get('q', '').strip()
    for tipo in tipos:
        qs = Equipo.objects.filter(profesionalidad__iexact=tipo)
        if q:
            qs = qs.filter(
                models.Q(nombre__icontains=q) | models.Q(profesionalidad__icontains=q)
            )
        equipos_agrupados[tipo] = qs.order_by('nombre')
    otros = Equipo.objects.exclude(profesionalidad__in=tipos)
    if q:
        otros = otros.filter(
            models.Q(nombre__icontains=q) | models.Q(profesionalidad__icontains=q)
        )
    equipos_agrupados['Otros'] = otros.order_by('nombre')
    return render(request, 'core/equipo.html', {'equipos_agrupados': equipos_agrupados})

def noticias(request):
    noticias = Noticia.objects.order_by('-fecha')
    return render(request, 'core/noticias.html', {'noticias': noticias})

def investigacion(request):
    investigaciones = Investigacion.objects.order_by('-fecha')
    return render(request, 'core/investigacion.html', {'investigaciones': investigaciones})

def publicaciones(request):
    publicaciones = Publicacion.objects.order_by('-fecha')
    return render(request, 'core/publicaciones.html', {'publicaciones': publicaciones})

def bolsa_trabajo(request):
    ofertas = BolsaTrabajo.objects.order_by('-fecha')
    return render(request, 'core/bolsa_trabajo.html', {'ofertas': ofertas})

def eventos(request):
    eventos = Evento.objects.order_by('-fecha')
    return render(request, 'core/eventos.html', {'eventos': eventos})

def contacto(request):
    return render(request, 'core/contacto.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('panel_equipo')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('panel_equipo')
    else:
        form = CustomLoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def panel_equipo(request):
    equipo = Equipo.objects.all()
    return render(request, 'core/panel_equipo.html', {'equipo': equipo})

@login_required
def equipo_add(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Integrante agregado correctamente.')
            return redirect('panel_equipo')
    else:
        form = EquipoForm()
    return render(request, 'core/equipo_form.html', {'form': form, 'accion': 'Agregar'})

@login_required
def equipo_edit(request, pk):
    persona = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=persona)
        if form.is_valid():
            form.save()
            messages.success(request, 'Integrante actualizado correctamente.')
            return redirect('panel_equipo')
    else:
        form = EquipoForm(instance=persona)
    return render(request, 'core/equipo_form.html', {'form': form, 'accion': 'Editar'})

@login_required
def equipo_delete(request, pk):
    persona = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        persona.delete()
        messages.success(request, 'Integrante eliminado correctamente.')
        return redirect('panel_equipo')
    return render(request, 'core/equipo_confirm_delete.html', {'persona': persona})

@login_required
def panel_noticias(request):
    noticias = Noticia.objects.order_by('-fecha')
    return render(request, 'core/panel_noticias.html', {'noticias': noticias})

@login_required
def noticia_add(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Noticia agregada correctamente.')
            return redirect('panel_noticias')
    else:
        form = NoticiaForm()
    return render(request, 'core/noticia_form.html', {'form': form, 'accion': 'Agregar'})

@login_required
def noticia_edit(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Noticia actualizada correctamente.')
            return redirect('panel_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'core/noticia_form.html', {'form': form, 'accion': 'Editar'})

@login_required
def noticia_delete(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        noticia.delete()
        messages.success(request, 'Noticia eliminada correctamente.')
        return redirect('panel_noticias')
    return render(request, 'core/noticia_confirm_delete.html', {'noticia': noticia})

@login_required
def panel_investigacion(request):
    investigaciones = Investigacion.objects.order_by('-fecha')
    return render(request, 'core/panel_investigacion.html', {'investigaciones': investigaciones})

@login_required
def investigacion_add(request):
    if request.method == 'POST':
        form = InvestigacionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Investigación agregada correctamente.')
            return redirect('panel_investigacion')
    else:
        form = InvestigacionForm()
    return render(request, 'core/investigacion_form.html', {'form': form, 'accion': 'Agregar'})

@login_required
def investigacion_edit(request, pk):
    investigacion = get_object_or_404(Investigacion, pk=pk)
    if request.method == 'POST':
        form = InvestigacionForm(request.POST, request.FILES, instance=investigacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Investigación actualizada correctamente.')
            return redirect('panel_investigacion')
    else:
        form = InvestigacionForm(instance=investigacion)
    return render(request, 'core/investigacion_form.html', {'form': form, 'accion': 'Editar'})

@login_required
def investigacion_delete(request, pk):
    investigacion = get_object_or_404(Investigacion, pk=pk)
    if request.method == 'POST':
        investigacion.delete()
        messages.success(request, 'Investigación eliminada correctamente.')
        return redirect('panel_investigacion')
    return render(request, 'core/investigacion_confirm_delete.html', {'investigacion': investigacion})

@login_required
def panel_publicaciones(request):
    publicaciones = Publicacion.objects.order_by('-fecha')
    return render(request, 'core/panel_publicaciones.html', {'publicaciones': publicaciones})

@login_required
def publicacion_add(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        imagenes = request.FILES.getlist('imagenes')
        if form.is_valid():
            publicacion = form.save()
            for idx, img in enumerate(imagenes):
                PublicacionImagen.objects.create(publicacion=publicacion, imagen=img, orden=idx)
            messages.success(request, 'Publicación agregada correctamente.')
            return redirect('panel_publicaciones')
    else:
        form = PublicacionForm()
    return render(request, 'core/publicacion_form.html', {'form': form, 'accion': 'Agregar'})

@login_required
def publicacion_edit(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES, instance=publicacion)
        imagenes = request.FILES.getlist('imagenes')
        if form.is_valid():
            form.save()
            for idx, img in enumerate(imagenes):
                PublicacionImagen.objects.create(publicacion=publicacion, imagen=img, orden=idx)
            messages.success(request, 'Publicación actualizada correctamente.')
            return redirect('panel_publicaciones')
    else:
        form = PublicacionForm(instance=publicacion)
    return render(request, 'core/publicacion_form.html', {'form': form, 'accion': 'Editar', 'publicacion': publicacion})

@login_required
def publicacion_delete(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, 'Publicación eliminada correctamente.')
        return redirect('panel_publicaciones')
    return render(request, 'core/publicacion_confirm_delete.html', {'publicacion': publicacion})

@login_required
def panel_eventos(request):
    eventos = Evento.objects.order_by('-fecha')
    return render(request, 'core/panel_eventos.html', {'eventos': eventos})

@login_required
def evento_add(request):
    from .forms import EventoForm
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento agregado correctamente.')
            return redirect('panel_eventos')
    else:
        form = EventoForm()
    return render(request, 'core/evento_form.html', {'form': form})

@login_required
def evento_edit(request, pk):
    from .forms import EventoForm
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento actualizado correctamente.')
            return redirect('panel_eventos')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'core/evento_form.html', {'form': form, 'evento': evento})

@login_required
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento eliminado correctamente.')
        return redirect('panel_eventos')
    return render(request, 'core/evento_confirm_delete.html', {'evento': evento})

@login_required
def evento_detalle(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    return render(request, 'core/evento_detalle.html', {'evento': evento})
