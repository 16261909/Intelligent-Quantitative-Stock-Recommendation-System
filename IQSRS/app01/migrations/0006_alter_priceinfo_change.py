# Generated by Django 4.0.6 on 2022-07-24 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_priceinfo_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priceinfo',
            name='change',
            field=models.DecimalField(decimal_places=4, max_digits=6),
        ),
    ]
