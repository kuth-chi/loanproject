# Generated by Django 3.2.16 on 2023-03-20 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0021_auto_20230320_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='full_off_from',
            field=models.BigIntegerField(blank=True, default=3, null=True),
        ),
    ]
