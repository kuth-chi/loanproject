# Generated by Django 3.2.16 on 2023-02-27 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0004_alter_collateral_cus_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagecollateral',
            old_name='mortgage',
            new_name='collateral',
        ),
    ]
