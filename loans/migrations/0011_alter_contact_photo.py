# Generated by Django 4.2.1 on 2023-07-12 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0010_contact_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='contact_photos/'),
        ),
    ]
