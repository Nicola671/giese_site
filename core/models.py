# Modelos para usuarios, eventos, archivos, etc. se definirán aquí
from django.db import models

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    profesionalidad = models.CharField(
        max_length=100,
        help_text="Ejemplo: Profesor/a, Preceptor/a, Director/a, etc.",
        blank=True
    )
    descripcion = models.TextField(blank=True)
    foto = models.ImageField(upload_to='equipo/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.profesionalidad or self.descripcion[:20]}"

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)
    
    def __str__(self):
        return self.titulo

class Investigacion(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='investigacion/fotos/', blank=True, null=True)
    archivo = models.FileField(upload_to='investigacion/', blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo

class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    autores = models.CharField(max_length=200)
    resumen = models.TextField()
    imagen = models.ImageField(upload_to='publicaciones/imagenes/', blank=True, null=True)
    video = models.FileField(upload_to='publicaciones/videos/', blank=True, null=True, help_text='Opcional. Solo formatos mp4/webm')
    archivo = models.FileField(upload_to='publicaciones/', blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo

class PublicacionImagen(models.Model):
    publicacion = models.ForeignKey(Publicacion, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='publicaciones/imagenes/')
    orden = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Imagen de {self.publicacion.titulo} ({self.id})"

class BolsaTrabajo(models.Model):
    puesto = models.CharField(max_length=200)
    descripcion = models.TextField()
    empresa = models.CharField(max_length=200)
    contacto = models.EmailField()
    archivo = models.FileField(upload_to='bolsa_trabajo/', blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.puesto} - {self.empresa}"

class Evento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField()
    fecha_cierre = models.DateField(null=True, blank=True, help_text="Fecha de cierre del evento (opcional)")
    pdf = models.FileField(upload_to='eventos/', blank=True, null=True, help_text="Archivo PDF del evento")
    archivo = models.FileField(upload_to='eventos/', blank=True, null=True, help_text="Archivos adicionales para descargar")
    
    def __str__(self):
        return self.nombre

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.email}"
