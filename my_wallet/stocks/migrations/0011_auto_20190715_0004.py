# Generated by Django 2.1.5 on 2019-07-14 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0010_auto_20190714_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prices',
            name='date_price',
            field=models.DateField(),
        ),
    ]