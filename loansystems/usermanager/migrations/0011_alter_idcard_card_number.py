# Generated by Django 3.2.16 on 2023-03-02 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0010_loan_laon_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idcard',
            name='card_number',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]
