# Generated by Django 4.2.14 on 2024-08-06 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('point', models.FloatField()),
                ('city', models.CharField(max_length=100)),
                ('cuisine', models.CharField(max_length=100)),
            ],
        ),
    ]
