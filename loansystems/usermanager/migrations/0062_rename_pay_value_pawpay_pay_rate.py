# Generated by Django 4.2 on 2023-05-30 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0061_remove_usersetting_is_navbar'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pawpay',
            old_name='pay_value',
            new_name='pay_rate',
        ),
    ]
