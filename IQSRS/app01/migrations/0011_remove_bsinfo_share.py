# Generated by Django 4.0.6 on 2022-07-24 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0010_remove_bsinfo_sid_remove_bsinfo_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bsinfo',
            name='share',
        ),
    ]