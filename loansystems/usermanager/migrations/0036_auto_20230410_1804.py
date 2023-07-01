# Generated by Django 3.2.16 on 2023-04-10 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0035_paw_pawpay'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paw',
            name='is_image',
        ),
        migrations.AlterField(
            model_name='paw',
            name='paw_status',
            field=models.CharField(blank=True, choices=[('active', 'active'), ('refunded', 'refunded'), ('expired', 'expired')], default='active', max_length=20),
        ),
    ]