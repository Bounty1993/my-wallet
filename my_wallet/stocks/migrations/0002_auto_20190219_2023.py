# Generated by Django 2.1.5 on 2019-02-19 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prices',
            options={'get_latest_by': 'date_price', 'ordering': ('-date_price',)},
        ),
    ]
