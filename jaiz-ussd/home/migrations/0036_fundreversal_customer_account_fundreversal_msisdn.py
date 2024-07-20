# Generated by Django 4.0.3 on 2022-06-26 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0035_fundreversal'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundreversal',
            name='customer_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.customeraccount'),
        ),
        migrations.AddField(
            model_name='fundreversal',
            name='msisdn',
            field=models.CharField(max_length=20, null=True),
        ),
    ]