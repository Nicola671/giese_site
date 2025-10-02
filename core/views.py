from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db import models

from .models import (
    Equipo, Noticia, NoticiaImagen, 
    Investigacion, InvestigacionFoto, InvestigacionArchivo, InvestigacionIntegrante,
    Publicacion, PublicacionImagen, PublicacionVideo, PublicacionArchivo, Evento, EventoArchivo,
    Universidad, TemaInteres, Profesionalidad, EquipoUniversidad, EquipoInteres
)
from .forms import EquipoForm, CustomLoginForm, NoticiaForm, InvestigacionForm, PublicacionForm

def inicio(request):
    quienes_somos = (
        "Somos GIESE, un grupo de investigación y extensión de la "
        "Universidad Nacional de Mar del Plata."
    )
    return render(request, "core/inicio.html", {"quienes_somos": quienes_somos})


def equipo(request):
    q = request.GET.get("q", "").strip()
    
    equipo_qs = Equipo.objects.all().order_by("nombre")

    if q:
        equipo_qs = equipo_qs.filter(
            models.Q(nombre__icontains=q) |
            models.Q(profesionalidades__titulo__icontains=q)
        ).distinct()

    return render(request, "core/equipo.html", {"equipo_completo": equipo_qs})


def equipo_detalle(request, pk):
    persona = get_object_or_404(Equipo, pk=pk)
    context = {
        'persona': persona
    }
    return render(request, "core/equipo_detalle.html", context)


def noticias(request):
    noticias = Noticia.objects.order_by("-fecha")
    return render(request, "core/noticias.html", {"noticias": noticias})


def investigacion(request):
    investigaciones = Investigacion.objects.order_by("-fecha")
    return render(request, "core/investigacion.html", {"investigaciones": investigaciones})


def investigacion_detalle(request, pk):
    investigacion = get_object_or_404(Investigacion, pk=pk)
    context = {
        'investigacion': investigacion
    }
    return render(request, "core/investigacion_detalle.html", context)


def publicaciones(request):
    publicaciones = Publicacion.objects.order_by("-fecha")
    return render(request, "core/publicaciones.html", {"publicaciones": publicaciones})


def publicacion_detalle(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    return render(request, "core/publicacion_detalle.html", {"publicacion": publicacion})


def eventos(request):
    eventos = Evento.objects.order_by("-fecha").prefetch_related("archivos")
    # compute cover image from first image-like related file
    for e in eventos:
        cover = None
        for a in e.archivos.all():
            try:
                url = a.archivo.url
            except Exception:
                url = ""
            lower = (url or "").lower()
            if lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                cover = url
                break
        e.cover_url = cover
    return render(request, "core/eventos.html", {"eventos": eventos})


def contacto(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        email = (request.POST.get("email") or "").strip()
        mensaje = (request.POST.get("mensaje") or "").strip()

        if not (nombre and email and mensaje):
            messages.error(request, "Completá todos los campos.")
            return render(request, "core/contacto.html", {"form_data": request.POST})

        from django.core.mail import send_mail
        from django.conf import settings

        subject = f"Nuevo mensaje de contacto - {nombre}"
        body = (
            f"Nombre: {nombre}\n"
            f"Email: {email}\n\n"
            f"Mensaje:\n{mensaje}"
        )
        recipient = ["gieseunmdp@gmail.com"]
        sender = getattr(settings, "DEFAULT_FROM_EMAIL", email or "no-reply@example.com")
        try:
            send_mail(subject, body, sender, recipient, fail_silently=False)
            messages.success(request, "Tu mensaje fue enviado. ¡Gracias por contactarnos!")
            return redirect("core:contacto")
        except Exception as e:
            messages.error(request, f"No se pudo enviar el mensaje: {e}")
            return render(request, "core/contacto.html", {"form_data": request.POST})

    return render(request, "core/contacto.html")


# ------------------ Autenticación ------------------

def _redirect_after_login(request, fallback="core:panel_equipo"):
    """
    Respeta ?next=/ruta/ si viene en GET/POST.
    Si next es una ruta absoluta (empieza con '/'), redirige a esa ruta.
    Si no, usa el nombre de URL de fallback.
    """
    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect(fallback)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:panel_equipo")

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return _redirect_after_login(request)
    else:
        form = CustomLoginForm()

    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("core:login")


# ------------------ Panel / CRUD: Equipo ------------------

@login_required
def panel_equipo(request):
    equipo_qs = Equipo.objects.order_by("nombre")
    return render(request, "core/panel_equipo_list.html", {"equipo": equipo_qs})


@login_required
def equipo_add(request):
    # Si el método es POST, procesamos el formulario. Si es GET, creamos uno vacío.
    if request.method == "POST":
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                obj = form.save()

                # --- Lógica para guardar campos dinámicos ---

                # 1. Guardar Profesionalidades (Roles)
                titulos = request.POST.getlist('profesionalidad_titulo')
                descripciones_prof = request.POST.getlist('profesionalidad_descripcion')
                
                Profesionalidad.objects.filter(equipo=obj).delete() # Limpiar roles antiguos
                for i, titulo in enumerate(titulos):
                    if titulo:
                        Profesionalidad.objects.create(
                            equipo=obj,
                            titulo=titulo,
                            descripcion=descripciones_prof[i],
                            orden=i + 1
                        )

                # 2. Guardar Universidades
                universidad_nombres = request.POST.getlist('universidad_nombre')
                descripciones_uni = request.POST.getlist('universidad_descripcion')

                EquipoUniversidad.objects.filter(equipo=obj).delete() # Limpiar universidades antiguas
                for i, nombre_uni in enumerate(universidad_nombres):
                    if nombre_uni:
                        # Busca o crea la universidad y obtén el objeto
                        universidad_obj, created = Universidad.objects.get_or_create(
                            descripcion_universidad=nombre_uni.strip()
                        )
                        EquipoUniversidad.objects.create(
                            equipo=obj,
                            universidad=universidad_obj,
                            descripcion=descripciones_uni[i],
                            orden=i + 1
                        )

                # 3. Guardar Temas de Interés
                interes_nombres = request.POST.getlist('interes_nombre')
                descripciones_interes = request.POST.getlist('interes_descripcion')

                EquipoInteres.objects.filter(equipo=obj).delete() # Limpiar intereses antiguos
                for i, nombre_interes in enumerate(interes_nombres):
                    if nombre_interes:
                        # Busca o crea el tema de interés y obtén el objeto
                        interes_obj, created = TemaInteres.objects.get_or_create(
                            descripcion_interes=nombre_interes.strip()
                        )
                        EquipoInteres.objects.create(
                            equipo=obj,
                            tema_interes=interes_obj,
                            descripcion=descripciones_interes[i],
                            orden=i + 1
                        )

                if not obj.user_id:
                    obj.user = request.user
                    obj.save(update_fields=["user"])
                
                # Manejar la foto si subieron un archivo
                foto_archivo = form.cleaned_data.get('foto_archivo')
                if foto_archivo:
                    # Por ahora guardamos el archivo temporalmente en el directorio media
                    import os
                    import uuid
                    from django.conf import settings
                    
                    # Crear directorio si no existe
                    media_dir = os.path.join(settings.MEDIA_ROOT, 'equipo_fotos')
                    os.makedirs(media_dir, exist_ok=True)
                    
                    # Generar nombre único
                    ext = foto_archivo.name.split('.')[-1]
                    filename = f"{obj.pk}_{obj.nombre.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.{ext}"
                    file_path = os.path.join(media_dir, filename)
                    
                    # Guardar archivo
                    with open(file_path, 'wb+') as destination:
                        for chunk in foto_archivo.chunks():
                            destination.write(chunk)
                    
                    # Actualizar URL en el modelo
                    relative_url = f"equipo_fotos/{filename}"
                    obj.foto = relative_url
                    obj.save()
                
                messages.success(request, f"✅ Integrante {obj.nombre} agregado correctamente al equipo.")
                return redirect("core:panel_equipo")
                
            except Exception as e:
                messages.error(request, f"❌ Error al agregar el integrante: {str(e)}")
                # Si hay un error al guardar, se mostrará el formulario con los datos y el mensaje.
    else:
        form = EquipoForm() # Formulario vacío para una nueva entrada
        
    # Preparamos dynamic_data para prellenar el formulario (ADD)
    dynamic_data = {}
    if request.method == "POST" and not form.is_valid():
        # Volvemos a mostrar lo que el usuario envió
        dynamic_data = {
            'profesionalidades': list(zip(request.POST.getlist('profesionalidad_titulo'), request.POST.getlist('profesionalidad_descripcion'))),
            'universidades': list(zip(request.POST.getlist('universidad_nombre'), request.POST.getlist('universidad_descripcion'))),
            'intereses': list(zip(request.POST.getlist('interes_nombre'), request.POST.getlist('interes_descripcion'))),
        }
    elif request.method == "GET":
        # Una fila vacía por sección para el alta
        dynamic_data = {
            'profesionalidades': [("", "")],
            'universidades': [("", "")],
            'intereses': [("", "")],
        }

    context = {
        "form": form, 
        "accion": "Agregar",
        "dynamic_data": dynamic_data,
    }
    return render(request, "core/equipo_form.html", context)


@login_required
def equipo_edit(request, pk):
    persona = get_object_or_404(Equipo, pk=pk)
    if request.method == "POST":
        form = EquipoForm(request.POST, request.FILES, instance=persona)
        if form.is_valid(): # Si el formulario es válido, se guarda
            try:
                obj = form.save()

                # --- Lógica para guardar campos dinámicos ---

                # 1. Guardar Profesionalidades (Roles)
                titulos = request.POST.getlist('profesionalidad_titulo')
                descripciones_prof = request.POST.getlist('profesionalidad_descripcion')
                
                Profesionalidad.objects.filter(equipo=obj).delete() # Limpiar roles antiguos
                for i, titulo in enumerate(titulos):
                    if titulo:
                        Profesionalidad.objects.create(
                            equipo=obj,
                            titulo=titulo,
                            descripcion=descripciones_prof[i],
                            orden=i + 1
                        )

                # 2. Guardar Universidades
                universidad_nombres = request.POST.getlist('universidad_nombre')
                descripciones_uni = request.POST.getlist('universidad_descripcion')

                EquipoUniversidad.objects.filter(equipo=obj).delete() # Limpiar universidades antiguas
                for i, nombre_uni in enumerate(universidad_nombres):
                    if nombre_uni:
                        universidad_obj, created = Universidad.objects.get_or_create(
                            descripcion_universidad=nombre_uni.strip()
                        )
                        EquipoUniversidad.objects.create(
                            equipo=obj,
                            universidad=universidad_obj,
                            descripcion=descripciones_uni[i],
                            orden=i + 1
                        )

                # 3. Guardar Temas de Interés
                interes_nombres = request.POST.getlist('interes_nombre')
                descripciones_interes = request.POST.getlist('interes_descripcion')

                EquipoInteres.objects.filter(equipo=obj).delete() # Limpiar intereses antiguos
                for i, nombre_interes in enumerate(interes_nombres):
                    if nombre_interes:
                        interes_obj, created = TemaInteres.objects.get_or_create(
                            descripcion_interes=nombre_interes.strip()
                        )
                        EquipoInteres.objects.create(
                            equipo=obj,
                            tema_interes=interes_obj,
                            descripcion=descripciones_interes[i],
                            orden=i + 1
                        )

                if not obj.user_id:
                    obj.user = request.user
                    obj.save(update_fields=["user"])
                
                # Manejar la foto si subieron un archivo nuevo
                foto_archivo = form.cleaned_data.get('foto_archivo')
                if foto_archivo:
                    import os
                    import uuid
                    from django.conf import settings
                    
                    # Crear directorio si no existe
                    media_dir = os.path.join(settings.MEDIA_ROOT, 'equipo_fotos')
                    os.makedirs(media_dir, exist_ok=True)
                    
                    # Generar nombre único
                    ext = foto_archivo.name.split('.')[-1]
                    filename = f"{obj.pk}_{obj.nombre.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.{ext}"
                    file_path = os.path.join(media_dir, filename)
                    
                    # Guardar archivo
                    with open(file_path, 'wb+') as destination:
                        for chunk in foto_archivo.chunks():
                            destination.write(chunk)
                    
                    # Actualizar URL en el modelo
                    relative_url = f"equipo_fotos/{filename}"
                    obj.foto = relative_url
                    obj.save()
                
                messages.success(request, f"✅ Información de {obj.nombre} actualizada correctamente.")
                return redirect("core:panel_equipo")
                
            except Exception as e:
                messages.error(request, f"❌ Error al actualizar: {str(e)}")
    else: # Si el método es GET, se crea el formulario con los datos de la persona
        form = EquipoForm(instance=persona)

    # Preparamos dynamic_data para prellenar el formulario (EDIT)
    dynamic_data = {}
    if request.method == "POST" and not form.is_valid():
        dynamic_data = {
            'profesionalidades': list(zip(request.POST.getlist('profesionalidad_titulo'), request.POST.getlist('profesionalidad_descripcion'))),
            'universidades': list(zip(request.POST.getlist('universidad_nombre'), request.POST.getlist('universidad_descripcion'))),
            'intereses': list(zip(request.POST.getlist('interes_nombre'), request.POST.getlist('interes_descripcion'))),
        }
    elif request.method == "GET":
        prof_list = [(p.titulo, (p.descripcion or "")) for p in persona.profesionalidades.order_by('orden', 'id')]
        uni_list = [
            (eu.universidad.descripcion_universidad, (eu.descripcion or ""))
            for eu in persona.equipo_universidades.order_by('orden', 'id')
        ]
        interes_list = [
            (ei.tema_interes.descripcion_interes, (ei.descripcion or ""))
            for ei in persona.equipo_intereses.order_by('orden', 'id')
        ]
        dynamic_data = {
            'profesionalidades': prof_list or [("", "")],
            'universidades': uni_list or [("", "")],
            'intereses': interes_list or [("", "")],
        }

    context = {
        "form": form, 
        "accion": "Editar",
        "persona": persona, # Pasamos la instancia para cargar datos existentes
        "dynamic_data": dynamic_data,
    }
    # Se renderiza la plantilla con el formulario (con datos o con errores)
    return render(request, "core/equipo_form.html", context)


@login_required
def equipo_delete(request, pk):
    persona = get_object_or_404(Equipo, pk=pk)
    if request.method == "POST":
        persona.delete()
        messages.success(request, "Integrante eliminado correctamente.")
        return redirect("core:panel_equipo")
    return render(request, "core/equipo_confirm_delete.html", {"persona": persona})


# ------------------ Panel / CRUD: Noticias ------------------

@login_required
def panel_noticias(request):
    noticias = Noticia.objects.order_by("-fecha")
    return render(request, "core/panel_noticias.html", {"noticias": noticias})


@login_required
def noticia_add(request):
    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if not obj.user_id:
                    obj.user = request.user
                obj.save()
                
                # Guardar imágenes adicionales (archivos subidos)
                imagenes_files = request.FILES.getlist('imagenes_adicionales')
                NoticiaImagen.objects.filter(noticia=obj).delete()  # Limpiar imágenes antiguas
                for i, img_file in enumerate(imagenes_files):
                    if img_file:
                        NoticiaImagen.objects.create(
                            noticia=obj,
                            imagen=img_file,
                            orden=i + 1
                        )
                
                messages.success(request, "✅ Noticia agregada correctamente.")
                return redirect("core:panel_noticias")
            except Exception as e:
                messages.error(request, f"❌ Error al agregar la noticia: {str(e)}")
    else:
        form = NoticiaForm()
    
    return render(request, "core/noticia_form.html", {
        "form": form, 
        "accion": "Agregar"
    })


@login_required
def noticia_edit(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if not obj.user_id:
                    obj.user = request.user
                obj.save()
                
                # Guardar imágenes adicionales (archivos subidos)
                imagenes_files = request.FILES.getlist('imagenes_adicionales')
                if imagenes_files:
                    # Solo limpiar si se subieron nuevas imágenes
                    NoticiaImagen.objects.filter(noticia=obj).delete()
                    for i, img_file in enumerate(imagenes_files):
                        if img_file:
                            NoticiaImagen.objects.create(
                                noticia=obj,
                                imagen=img_file,
                                orden=i + 1
                            )
                
                messages.success(request, "✅ Noticia actualizada correctamente.")
                return redirect("core:panel_noticias")
            except Exception as e:
                messages.error(request, f"❌ Error al actualizar la noticia: {str(e)}")
    else:
        form = NoticiaForm(instance=noticia)
    
    return render(request, "core/noticia_form.html", {
        "form": form, 
        "accion": "Editar",
        "noticia": noticia
    })


@login_required
def noticia_delete(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == "POST":
        noticia.delete()
        messages.success(request, "Noticia eliminada correctamente.")
        return redirect("core:panel_noticias")
    return render(request, "core/noticia_confirm_delete.html", {"noticia": noticia})


# ------------------ Panel / CRUD: Investigación ------------------

@login_required
def panel_investigacion(request):
    investigaciones = Investigacion.objects.order_by("-fecha")
    return render(request, "core/panel_investigacion.html", {"investigaciones": investigaciones})


@login_required
def investigacion_add(request):
    if request.method == "POST":
        form = InvestigacionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if not obj.user_id:
                    obj.user = request.user
                obj.save()
                
                # Guardar fotos
                fotos_files = request.FILES.getlist('fotos')
                for i, foto_file in enumerate(fotos_files):
                    if foto_file:
                        InvestigacionFoto.objects.create(
                            investigacion=obj,
                            foto=foto_file,
                            orden=i + 1
                        )
                
                # Guardar archivos (PDFs, etc.)
                archivos_files = request.FILES.getlist('archivos')
                archivos_nombres = request.POST.getlist('archivo_nombre')
                for i, archivo_file in enumerate(archivos_files):
                    if archivo_file:
                        nombre = archivos_nombres[i] if i < len(archivos_nombres) else archivo_file.name
                        InvestigacionArchivo.objects.create(
                            investigacion=obj,
                            archivo=archivo_file,
                            nombre=nombre,
                            orden=i + 1
                        )
                
                # Guardar integrantes
                integrantes_ids = request.POST.getlist('integrante_id')
                integrantes_roles = request.POST.getlist('integrante_rol')
                for i, integrante_id in enumerate(integrantes_ids):
                    if integrante_id:
                        rol = integrantes_roles[i] if i < len(integrantes_roles) else ''
                        InvestigacionIntegrante.objects.create(
                            investigacion=obj,
                            integrante_id=integrante_id,
                            rol=rol,
                            orden=i + 1
                        )
                
                messages.success(request, "✅ Investigación agregada correctamente.")
                return redirect("core:panel_investigacion")
            except Exception as e:
                messages.error(request, f"❌ Error al agregar la investigación: {str(e)}")
    else:
        form = InvestigacionForm()
    
    # Obtener todos los integrantes del equipo para el selector
    equipo_list = Equipo.objects.all().order_by('nombre')
    
    return render(request, "core/investigacion_form.html", {
        "form": form, 
        "accion": "Agregar",
        "equipo_list": equipo_list
    })


@login_required
def investigacion_edit(request, pk):
    investigacion = get_object_or_404(Investigacion, pk=pk)
    if request.method == "POST":
        form = InvestigacionForm(request.POST, request.FILES, instance=investigacion)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if not obj.user_id:
                    obj.user = request.user
                obj.save()
                
                # Guardar fotos nuevas
                fotos_files = request.FILES.getlist('fotos')
                if fotos_files:
                    InvestigacionFoto.objects.filter(investigacion=obj).delete()
                    for i, foto_file in enumerate(fotos_files):
                        if foto_file:
                            InvestigacionFoto.objects.create(
                                investigacion=obj,
                                foto=foto_file,
                                orden=i + 1
                            )
                
                # Guardar archivos nuevos
                archivos_files = request.FILES.getlist('archivos')
                archivos_nombres = request.POST.getlist('archivo_nombre')
                if archivos_files:
                    InvestigacionArchivo.objects.filter(investigacion=obj).delete()
                    for i, archivo_file in enumerate(archivos_files):
                        if archivo_file:
                            nombre = archivos_nombres[i] if i < len(archivos_nombres) else archivo_file.name
                            InvestigacionArchivo.objects.create(
                                investigacion=obj,
                                archivo=archivo_file,
                                nombre=nombre,
                                orden=i + 1
                            )
                
                # Actualizar integrantes
                integrantes_ids = request.POST.getlist('integrante_id')
                integrantes_roles = request.POST.getlist('integrante_rol')
                InvestigacionIntegrante.objects.filter(investigacion=obj).delete()
                for i, integrante_id in enumerate(integrantes_ids):
                    if integrante_id:
                        rol = integrantes_roles[i] if i < len(integrantes_roles) else ''
                        InvestigacionIntegrante.objects.create(
                            investigacion=obj,
                            integrante_id=integrante_id,
                            rol=rol,
                            orden=i + 1
                        )
                
                messages.success(request, "✅ Investigación actualizada correctamente.")
                return redirect("core:panel_investigacion")
            except Exception as e:
                messages.error(request, f"❌ Error al actualizar la investigación: {str(e)}")
    else:
        form = InvestigacionForm(instance=investigacion)
    
    # Obtener todos los integrantes del equipo para el selector
    equipo_list = Equipo.objects.all().order_by('nombre')
    
    return render(request, "core/investigacion_form.html", {
        "form": form, 
        "accion": "Editar",
        "investigacion": investigacion,
        "equipo_list": equipo_list
    })


@login_required
def investigacion_delete(request, pk):
    investigacion = get_object_or_404(Investigacion, pk=pk)
    if request.method == "POST":
        investigacion.delete()
        messages.success(request, "Investigación eliminada correctamente.")
        return redirect("core:panel_investigacion")
    return render(request, "core/investigacion_confirm_delete.html", {"investigacion": investigacion})


# ------------------ Panel / CRUD: Publicaciones ------------------

@login_required
def panel_publicaciones(request):
    publicaciones = Publicacion.objects.order_by("-fecha")
    return render(request, "core/panel_publicaciones.html", {"publicaciones": publicaciones})


@login_required
def publicacion_add(request):
    if request.method == "POST":
        form = PublicacionForm(request.POST)
        if form.is_valid():
            try:
                publicacion = form.save(commit=False)
                if not publicacion.user_id:
                    publicacion.user = request.user
                publicacion.save()

                # Guardar imágenes
                imagenes_files = request.FILES.getlist('imagenes')
                for i, img in enumerate(imagenes_files):
                    if img:
                        PublicacionImagen.objects.create(
                            publicacion=publicacion,
                            imagen=img,
                            orden=i + 1
                        )

                # Guardar videos
                videos_files = request.FILES.getlist('videos')
                for i, vid in enumerate(videos_files):
                    if vid:
                        PublicacionVideo.objects.create(
                            publicacion=publicacion,
                            video=vid,
                            orden=i + 1
                        )

                # Guardar archivos descargables
                archivos_files = request.FILES.getlist('archivos')
                archivos_nombres = request.POST.getlist('archivo_nombre')
                for i, f in enumerate(archivos_files):
                    if f:
                        nombre = archivos_nombres[i] if i < len(archivos_nombres) else f.name
                        PublicacionArchivo.objects.create(
                            publicacion=publicacion,
                            archivo=f,
                            nombre=nombre,
                            orden=i + 1
                        )

                messages.success(request, "✅ Publicación agregada correctamente.")
                return redirect("core:panel_publicaciones")
            except Exception as e:
                messages.error(request, f"❌ Error al agregar la publicación: {str(e)}")
    else:
        form = PublicacionForm()
    return render(request, "core/publicacion_form.html", {"form": form, "accion": "Agregar"})


@login_required
def publicacion_edit(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == "POST":
        form = PublicacionForm(request.POST, instance=publicacion)
        if form.is_valid():
            try:
                pub = form.save(commit=False)
                if not pub.user_id:
                    pub.user = request.user
                pub.save()

                # Reemplazar imágenes si subieron nuevas
                imagenes_files = request.FILES.getlist('imagenes')
                if imagenes_files:
                    PublicacionImagen.objects.filter(publicacion=pub).delete()
                    for i, img in enumerate(imagenes_files):
                        if img:
                            PublicacionImagen.objects.create(
                                publicacion=pub,
                                imagen=img,
                                orden=i + 1
                            )

                # Reemplazar videos si subieron nuevos
                videos_files = request.FILES.getlist('videos')
                if videos_files:
                    PublicacionVideo.objects.filter(publicacion=pub).delete()
                    for i, vid in enumerate(videos_files):
                        if vid:
                            PublicacionVideo.objects.create(
                                publicacion=pub,
                                video=vid,
                                orden=i + 1
                            )

                # Reemplazar archivos si subieron nuevos
                archivos_files = request.FILES.getlist('archivos')
                archivos_nombres = request.POST.getlist('archivo_nombre')
                if archivos_files:
                    PublicacionArchivo.objects.filter(publicacion=pub).delete()
                    for i, f in enumerate(archivos_files):
                        if f:
                            nombre = archivos_nombres[i] if i < len(archivos_nombres) else f.name
                            PublicacionArchivo.objects.create(
                                publicacion=pub,
                                archivo=f,
                                nombre=nombre,
                                orden=i + 1
                            )

                messages.success(request, "✅ Publicación actualizada correctamente.")
                return redirect("core:panel_publicaciones")
            except Exception as e:
                messages.error(request, f"❌ Error al actualizar la publicación: {str(e)}")
    else:
        form = PublicacionForm(instance=publicacion)
    return render(
        request,
        "core/publicacion_form.html",
        {"form": form, "accion": "Editar", "publicacion": publicacion},
    )


@login_required
def publicacion_delete(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == "POST":
        publicacion.delete()
        messages.success(request, "Publicación eliminada correctamente.")
        return redirect("core:panel_publicaciones")
    return render(request, "core/publicacion_confirm_delete.html", {"publicacion": publicacion})


# ------------------ Panel / CRUD: Eventos ------------------

@login_required
def panel_eventos(request):
    eventos = Evento.objects.order_by("-fecha")
    return render(request, "core/panel_eventos.html", {"eventos": eventos})


@login_required
def evento_add(request):
    from .forms import EventoForm
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if not obj.user_id:
                    obj.user = request.user
                obj.save()

                # Archivos múltiples
                archivos_files = request.FILES.getlist('archivos')
                archivos_nombres = request.POST.getlist('archivo_nombre')
                for i, f in enumerate(archivos_files):
                    if f:
                        nombre = archivos_nombres[i] if i < len(archivos_nombres) else f.name
                        EventoArchivo.objects.create(
                            evento=obj,
                            archivo=f,
                            nombre=nombre,
                            orden=i + 1
                        )

                messages.success(request, "Evento agregado correctamente.")
                return redirect("core:panel_eventos")
            except Exception as e:
                messages.error(request, f"Error al agregar: {e}")
    else:
        form = EventoForm()
    return render(request, "core/evento_form.html", {"form": form})


@login_required
def evento_edit(request, pk):
    from .forms import EventoForm
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if not obj.user_id:
                    obj.user = request.user
                obj.save()

                # Si se suben nuevos archivos, reemplazar los existentes
                archivos_files = request.FILES.getlist('archivos')
                archivos_nombres = request.POST.getlist('archivo_nombre')
                if archivos_files:
                    EventoArchivo.objects.filter(evento=obj).delete()
                    for i, f in enumerate(archivos_files):
                        if f:
                            nombre = archivos_nombres[i] if i < len(archivos_nombres) else f.name
                            EventoArchivo.objects.create(
                                evento=obj,
                                archivo=f,
                                nombre=nombre,
                                orden=i + 1
                            )

                messages.success(request, "Evento actualizado correctamente.")
                return redirect("core:panel_eventos")
            except Exception as e:
                messages.error(request, f"Error al actualizar: {e}")
    else:
        form = EventoForm(instance=evento)
    return render(request, "core/evento_form.html", {"form": form, "evento": evento})


@login_required
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == "POST":
        evento.delete()
        messages.success(request, "Evento eliminado correctamente.")
        return redirect("core:panel_eventos")
    return render(request, "core/evento_confirm_delete.html", {"evento": evento})


@login_required
def evento_detalle(request, pk):
    evento = get_object_or_404(Evento.objects.prefetch_related("archivos"), pk=pk)
    cover = None
    for a in evento.archivos.all():
        try:
            url = a.archivo.url
        except Exception:
            url = ""
        lower = (url or "").lower()
        if lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            cover = url
            break
    evento.cover_url = cover
    return render(request, "core/evento_detalle.html", {"evento": evento})
