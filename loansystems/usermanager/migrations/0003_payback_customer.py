# Generated by Django 3.2.16 on 2023-02-27 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0002_loan_loan_number_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payback',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='usermanager.customer'),
        ),
    ]
