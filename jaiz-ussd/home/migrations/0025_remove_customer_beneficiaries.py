# Generated by Django 4.0.2 on 2022-04-04 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_merge_20220404_1204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='beneficiaries',
        ),
    ]