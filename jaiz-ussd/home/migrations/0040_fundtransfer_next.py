# Generated by Django 4.0.3 on 2022-07-04 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0039_fundtransfer_bank_list_response_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundtransfer',
            name='next',
            field=models.IntegerField(null=True),
        ),
    ]