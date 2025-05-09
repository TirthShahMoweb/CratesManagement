# Generated by Django 5.2 on 2025-04-29 20:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crates', '0009_alter_collectioncenter_damage_crates_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectioncenter',
            name='floor_supervisor',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supervised_centers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='collectioncenter',
            name='zonal_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='managed_zones', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='loadout',
            name='collection_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crates.collectioncenter'),
        ),
        migrations.AlterField(
            model_name='loadout',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crates.warehouse'),
        ),
        migrations.AlterField(
            model_name='loadoutbunch',
            name='collection_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crates.collectioncenter'),
        ),
        migrations.AlterField(
            model_name='loadoutbunch',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crates.warehouse'),
        ),
        migrations.AlterField(
            model_name='truck',
            name='empty_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='truck',
            name='filled_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='container_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='operation_officer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
