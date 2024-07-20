# Generated by Django 4.0.2 on 2022-03-29 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_airtime_beneficiary'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundtransfer',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
    ]