# Generated by Django 2.2.4 on 2019-08-19 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0014_auto_20190819_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='prevShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
    ]