# Generated by Django 4.2.1 on 2023-06-26 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0007_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='data',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
