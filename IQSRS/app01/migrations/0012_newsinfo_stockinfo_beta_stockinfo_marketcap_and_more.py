# Generated by Django 4.0.6 on 2022-07-25 06:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0011_remove_bsinfo_share'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='stockinfo',
            name='beta',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='stockinfo',
            name='marketcap',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stockinfo',
            name='pe',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.CreateModel(
            name='NewsConn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.newsinfo', verbose_name='newsid')),
                ('sid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.stockinfo', verbose_name='stockid')),
            ],
        ),
    ]
