# Generated by Django 3.2.16 on 2023-03-01 08:11

from django.db import migrations, models
import django.db.models.deletion
import usermanager.models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0005_rename_mortgage_imagecollateral_collateral'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_type', models.CharField(blank=True, max_length=120)),
                ('card_number', models.BigIntegerField(blank=True)),
                ('card_deadline', models.DateField(blank=True)),
                ('name', models.IntegerField(blank=True, max_length=8)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.customer')),
            ],
        ),
        migrations.AlterField(
            model_name='imagecollateral',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=usermanager.models.upload_collateral_image),
        ),
        migrations.CreateModel(
            name='imageIdCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.ImageField(blank=True, null=True, upload_to=usermanager.models.upload_customer_image)),
                ('id_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.idcard')),
            ],
        ),
    ]