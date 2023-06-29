# Generated by Django 3.2.16 on 2023-03-17 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0017_auto_20230306_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='payback',
            name='status',
            field=models.CharField(blank=True, choices=[('paid', 'paid'), ('full paid', 'full paid')], default='paid', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='laon_status',
            field=models.CharField(blank=True, choices=[('on going', 'on going'), ('completed', 'completed'), ('lost', 'lost')], default='on going', max_length=20),
        ),
    ]
