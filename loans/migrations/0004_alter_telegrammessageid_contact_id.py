# Generated by Django 4.2.1 on 2023-05-24 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0003_telegrammessageid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrammessageid',
            name='contact_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
