# Generated by Django 4.0.3 on 2022-06-24 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0033_remove_item_package'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeraccount',
            name='amount',
            field=models.FloatField(default=0.0, max_length=20),
        ),
    ]
