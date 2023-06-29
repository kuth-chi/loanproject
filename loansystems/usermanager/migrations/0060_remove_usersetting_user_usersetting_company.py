# Generated by Django 4.2 on 2023-05-29 01:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0059_usersetting_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersetting',
            name='user',
        ),
        migrations.AddField(
            model_name='usersetting',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usermanager.company'),
            preserve_default=False,
        ),
    ]
