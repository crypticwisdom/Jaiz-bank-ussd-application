# Generated by Django 4.0.1 on 2022-02-08 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_customer_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerpin',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='home.customer'),
        ),
    ]
