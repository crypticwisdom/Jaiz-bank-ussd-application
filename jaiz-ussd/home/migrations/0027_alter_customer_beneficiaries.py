# Generated by Django 4.0.2 on 2022-04-04 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_customer_beneficiaries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='beneficiaries',
            field=models.ManyToManyField(blank=True, to='home.Beneficiary'),
        ),
    ]
