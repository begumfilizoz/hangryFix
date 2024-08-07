# Generated by Django 4.2.14 on 2024-08-06 11:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testdb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('description', models.CharField(max_length=300)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testdb.restaurant')),
            ],
        ),
    ]
