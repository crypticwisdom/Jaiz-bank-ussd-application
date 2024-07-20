# Generated by Django 4.0.1 on 2022-02-13 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_customer_has_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemporalList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('account_no', models.CharField(default='', max_length=200, null=True, unique=True)),
            ],
        ),
    ]
