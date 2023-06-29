# Generated by Django 4.2 on 2023-05-24 07:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import usermanager.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usermanager', '0055_borrowpayback_total_pay'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dep_name', models.CharField(blank=True, max_length=150)),
                ('dep_desc', models.TextField(blank=True, max_length=350)),
                ('created_at', models.DateField(auto_now=True)),
                ('update_at', models.DateField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.company')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('profile', models.ImageField(default='static/img/profile_image_defautl.png', upload_to=usermanager.models.upload_logo_profile)),
                ('id_number', models.CharField(editable=False, max_length=8, unique=True)),
                ('street', models.CharField(blank=True, max_length=100)),
                ('gender', models.CharField(blank=True, max_length=20)),
                ('birth_date', models.DateField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('join_date', models.DateField(auto_now=True)),
                ('time_zone', models.CharField(default='UTC', max_length=128)),
                ('created_at', models.DateField(auto_now=True)),
                ('update_at', models.DateField(auto_now=True)),
                ('commune', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.commune')),
                ('country', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.country')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.department')),
                ('district', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.district')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ps_name', models.CharField(blank=True, max_length=150)),
                ('ps_desc', models.TextField(blank=True, max_length=350)),
                ('created_at', models.DateField(auto_now=True)),
                ('update_at', models.DateField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.company')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.department')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.company')),
                ('emp_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.employeedetail')),
            ],
        ),
        migrations.AddField(
            model_name='employeedetail',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.position'),
        ),
        migrations.AddField(
            model_name='employeedetail',
            name='province',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.province'),
        ),
        migrations.AddField(
            model_name='employeedetail',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='employeedetail',
            name='village',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='usermanager.village'),
        ),
    ]
