# Generated by Django 4.1 on 2023-03-18 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0062_alter_data_data_amount'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bank',
        ),
        migrations.AddField(
            model_name='fundtransfer',
            name='pin_tries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fundtransfer',
            name='receiver_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
