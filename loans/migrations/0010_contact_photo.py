# Generated by Django 4.2.1 on 2023-07-11 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0009_notification_transaction_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='contact_photos'),
        ),
    ]
# Generated by Django 4.2.1 on 2023-07-12 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0009_notification_transaction_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='contact_photos'),
        ),
    ]
