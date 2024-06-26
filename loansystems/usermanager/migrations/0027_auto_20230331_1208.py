# Generated by Django 3.2.16 on 2023-03-31 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0026_companyaddress_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_account_currency',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_account_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
