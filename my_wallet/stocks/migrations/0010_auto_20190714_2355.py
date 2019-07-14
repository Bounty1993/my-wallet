# Generated by Django 2.1.5 on 2019-07-14 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0009_auto_20190603_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prices',
            name='date_price',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='prices',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True),
        ),
    ]