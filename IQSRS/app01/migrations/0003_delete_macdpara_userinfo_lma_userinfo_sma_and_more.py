# Generated by Django 4.0.6 on 2022-07-24 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_alter_userinfo_createtime'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MACDPara',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='lma',
            field=models.SmallIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='sma',
            field=models.SmallIntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='btinfo',
            name='paraid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.strinfo', verbose_name='parameterid'),
        ),
    ]