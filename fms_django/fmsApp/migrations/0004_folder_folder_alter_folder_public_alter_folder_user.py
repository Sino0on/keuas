# Generated by Django 4.0.3 on 2022-12-18 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fmsApp', '0003_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='fmsApp.folder'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='public',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='folder',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]