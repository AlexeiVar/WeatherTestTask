# Generated by Django 5.1.1 on 2025-05-26 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CheckedCity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.TextField()),
                ('date', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CityCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.TextField()),
                ('count', models.IntegerField()),
            ],
        ),
    ]
