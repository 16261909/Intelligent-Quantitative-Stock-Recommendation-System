# Generated by Django 4.0.6 on 2022-07-24 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_delete_macdpara_userinfo_lma_userinfo_sma_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='btinfo',
            name='startcash',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='lma',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='sma',
        ),
        migrations.AddField(
            model_name='strinfo',
            name='paraf1',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='paraf2',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='parai1',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='parai2',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='parai3',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='parai4',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='parai5',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strinfo',
            name='startcash',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
    ]
