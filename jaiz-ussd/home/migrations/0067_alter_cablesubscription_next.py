# Generated by Django 4.1 on 2023-03-20 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0066_alter_cablesubscription_next'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cablesubscription',
            name='next',
            field=models.IntegerField(blank=True, default=1, max_length=10, null=True),
        ),
    ]
