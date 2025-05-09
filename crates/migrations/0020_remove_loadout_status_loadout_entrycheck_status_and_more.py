# Generated by Django 5.2 on 2025-05-02 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crates', '0019_loadout_sg_exit_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loadout',
            name='status',
        ),
        migrations.AddField(
            model_name='loadout',
            name='entrycheck_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('REJECTED', 'Rejected'), ('APPROVED', 'Approved')], default='PENDING', max_length=50),
        ),
        migrations.AddField(
            model_name='loadout',
            name='truck_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('COMING', 'Coming'), ('ENTRY_CHECKED', 'Entry Checked'), ('UNLOADED', 'Unloaded'), ('EXITED', 'Exited')], default='PENDING', max_length=50),
        ),
    ]
