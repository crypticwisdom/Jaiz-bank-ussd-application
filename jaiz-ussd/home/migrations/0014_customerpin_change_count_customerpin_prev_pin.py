# Generated by Django 4.0.1 on 2022-02-17 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_customerpin_last_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerpin',
            name='change_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customerpin',
            name='prev_pin',
            field=models.CharField(default='', max_length=100),
        ),
    ]