from django.db import models 
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class CustomUser(User):
    is_logged_in = models.BooleanField(default=False)


class Contact(models.Model):
    name = models.CharField(max_length=45)
    number = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.name} ({self.number})'


TRANSACTION_CHOICE = (
    ('borrow', 'Взять в долг'),
    ('repay', 'Погасить займ'),
    ('lend', 'Дать в долг'),
    ('receive', 'Принять погашение'),
)

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    data = models.DateTimeField(null=True, blank=True)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_CHOICE, default='borrow', verbose_name='Transaction type')
    comment = models.CharField(max_length=500, null=True, blank=True)


TELEGRAM_ACTION_CHOICE = (
    ('add_contact', 'Добавить контакт'),
    ('borrow', 'Взять в долг'),
    ('repay', 'Погасить займ'),
    ('lend', 'Дать в долг'),
    ('receive', 'Принять погашение'),
    ('register', 'Регистрация'),

)

class TelegramMessageId(models.Model):
    chat_id = models.CharField(max_length=25)
    message_id = models.CharField(max_length=25)
    action = models.CharField(
        max_length=15, 
        choices=TELEGRAM_ACTION_CHOICE, 
        default='borrow')
    contact_id = models.IntegerField(blank=True,null=True)

class Notification(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, primary_key=True)
    repayment_date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.repayment_date:
            # Вычисляем дату погашения на основе текущей даты и срока погашения транзакции
            self.repayment_date = timezone.now().date() + timedelta(days=self.transaction.contact.days)
        super().save(*args, **kwargs)    
