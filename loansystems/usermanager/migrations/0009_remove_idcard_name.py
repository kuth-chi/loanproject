# Generated by Django 3.2.16 on 2023-03-01 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0008_auto_20230301_1517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='idcard',
            name='name',
        ),
    ]