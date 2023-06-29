# Generated by Django 4.2 on 2023-05-03 04:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usermanager', '0044_pawpay_remaining'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paw',
            name='is_principle',
        ),
        migrations.RemoveField(
            model_name='paw',
            name='paw_period_principle',
        ),
        migrations.RemoveField(
            model_name='paw',
            name='paw_principle_cycle',
        ),
        migrations.CreateModel(
            name='PawBorrow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paw_borrow_status', models.CharField(blank=True, choices=[('active', 'active'), ('refunded', 'refunded'), ('expired', 'expired')], default='active', max_length=20)),
                ('paw_borrow_method', models.CharField(blank=True, choices=[('day', 'day'), ('week', 'week'), ('month', 'month'), ('year', 'year')], default='day', max_length=20)),
                ('paw_borrow_value', models.DecimalField(blank=True, decimal_places=2, max_digits=20)),
                ('paw_borrow_type', models.CharField(blank=True, max_length=200)),
                ('is_percentage', models.BooleanField(default=False)),
                ('borrow_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=20)),
                ('date_borrow', models.DateField()),
                ('date_expired_borrow', models.DateField()),
                ('is_principle', models.BooleanField(default=False)),
                ('paw_borrow_principle_cycle', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paw_borrow_period_principle', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
                ('paw', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usermanager.paw')),
            ],
        ),
    ]
