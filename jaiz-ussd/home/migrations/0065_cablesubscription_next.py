# Generated by Django 4.1 on 2023-03-20 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0064_alter_item_charges'),
    ]

    operations = [
        migrations.AddField(
            model_name='cablesubscription',
            name='next',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]