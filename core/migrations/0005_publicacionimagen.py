# Generated by Django 5.2.4 on 2025-07-03 02:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_publicacion_imagen_publicacion_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicacionImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='publicaciones/imagenes/')),
                ('orden', models.PositiveIntegerField(default=0)),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='core.publicacion')),
            ],
        ),
    ]
