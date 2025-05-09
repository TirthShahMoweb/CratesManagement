# Generated by Django 5.2 on 2025-04-30 12:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crates', '0011_alter_truck_total_crates'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='warehouse_manager',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='managed_warehouses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='operation_officer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
