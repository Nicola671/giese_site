# Generated by Django 5.2.4 on 2025-07-03 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipo',
            name='cargo',
        ),
        migrations.AddField(
            model_name='equipo',
            name='profesionalidad',
            field=models.CharField(blank=True, help_text='Ejemplo: Profesor/a, Preceptor/a, Director/a, etc.', max_length=100),
        ),
    ]
