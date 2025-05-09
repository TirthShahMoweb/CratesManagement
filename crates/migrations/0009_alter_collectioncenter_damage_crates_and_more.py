# Generated by Django 5.2 on 2025-04-29 20:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crates', '0008_loadout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectioncenter',
            name='damage_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectioncenter',
            name='empty_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectioncenter',
            name='filled_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectioncenter',
            name='floor_supervisor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='supervised_centers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='collectioncenter',
            name='missing_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectioncenter',
            name='total_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='damage_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='empty_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='filled_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='missing_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='ready_to_sell_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='total_crates',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
