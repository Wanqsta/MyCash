# Generated by Django 4.2.1 on 2023-05-24 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0002_rename_creadet_contact_credit_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramMessageId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=25)),
                ('message_id', models.CharField(max_length=25)),
                ('action', models.CharField(choices=[('add_contact', 'Добавить контакт'), ('borrow', 'Взять в долг'), ('repay', 'Погасить займ'), ('lend', 'Дать в долг'), ('receive', 'Принять погашение'), ('register', 'Регистрация')], default='borrow', max_length=15)),
                ('contact_id', models.IntegerField()),
            ],
        ),
    ]
