from .math import calculate_total
from users.models import User
from loans.models import Transaction
from telebot import TeleBot, types

def my_profile(user_id):
    debit_total = calculate_total(user_id, 'debit')
    credit_total = calculate_total(user_id, 'credit')
    user = User.objects.get(id=user_id)
    username = user.username.split(':')[0]

    message = f"Информация о вас: {username} \nСумма дебитов: {debit_total}\nСумма кредитов: {credit_total}\n"
    return message

transaction_message = f'Для создания нового займа:\n1) Нажмите на кнопку "💸 Новый займ" в главном меню\n2) Выберите контакт, которому хотите изменить займ, и нажмите на него.\nЕсли вы не можете найти нужный вам контакт, то нажмите на кнопку "🔍 Поиск" в конце списка\nили создайте новый контакт нажав на кнопку "+ Контакт".'

search_instr = '''Кнопка "🔍 Быстрый поиск" нужна для быстрого доступа к основным функциям бота:\nНажмите на кнопку "Мне должны", чтобы увидеть список контактов, которые вам должны, и их общую сумму.\nНажмите на кнопку "Я должен", чтобы увидеть список контактов, которым вы должны, и их общую сумму.\nНажмите "+ Контакт", если хотите добавить новый контакт.\nНажмите кнопку "🔍 Поиск" для нахождения нужного вам контакта.'''

add_contact_message = '''Для добавления нового контакта выберите один из вариантов:\n1) Напишите имя и номер контакта через двоеточие "Имя:Номер"\n2) Добавьте контакт из своего списка контактов через кнопку в виде скрепки " 📎 "'''

def transaction_history(user_id):
    transactions = Transaction.objects.filter(contact__user_id=user_id).order_by('-created')
    if transactions.exists():
        history_message = "📖 История транзакций:\n"
        for transaction in transactions:
            created_formatted = transaction.created.strftime('%Y-%m-%d %H:%M')
            history_message += f"Контакт: {transaction.contact}\nТип транзакции: {transaction.transaction_type}\nКомментарий:{transaction.comment}\nСумма: {transaction.amount}\nДата: {created_formatted}\n\n"
    else:
        history_message = "У вас еще нет транзакций."

    return history_message

from datetime import datetime

def history(contact_id):
    transactions = Transaction.objects.filter(contact_id=contact_id).order_by('-created')
    if transactions.exists():
        history_message = "📖 История транзакций:\n" 
        for transaction in transactions:
            created_formatted = transaction.created.strftime('%Y-%m-%d %H:%M')
            history_message += f"Тип транзакции: {transaction.transaction_type}\nКомментарий:{transaction.comment}\nСумма: {transaction.amount}\nДата: {created_formatted}\n\n"
    else:
        history_message = "У вас еще нет транзакций."

    return history_message

register_instr = '''
Для регистрации:
Нажмите на кнопку "Sign Up" и следуйте указаниям.

Для входа в существующий аккаунт:
Нажмите на кнопку "Login" и следуйте указаниям.

Для смены аккаунта:
Нажмите /command2 для выхода из нынешнего аккаунта и следуйте указаниям выше

После успешной регистрации или входа в систему вы сможете использовать кнопки меню для управления ботом.
'''

add_contact_instr = '''Для добавления нового контакта нажмите на кнопку "+ Контакт", которая находиться в разделах "🔍 Быстрый поиск" и "💸 Новый займ"\nДалее выберите один из вариантов:\n1) Напишите имя и номер контакта через двоеточие "Имя:Номер"\n2) Отправьте контакт из своего списка контактов через кнопку в виде скрепки " 📎 "'''

history_instr = '''
Кнопка "📖 История транзакций" находится в разделе "👤 Мой профиль" в Главном меню
📖 История транзакций покажет вам все ваши взаимодействия с контактами по критериям: тип транзакции(вы отдали в займ, вам вернули займ, вы взяли в займ, вы вернули займ), сумма(которую отдали/взяли в тот момент), дата(когда и в какое время это произошло)

Также вы можете открыть 📖 Историю транзакций с определенным контактом, где будут показаны только ваши с ним взаимодействия. Для этого вам нужно нажать на контакт, с которым вы хотите увидеть историю транзакций, и внизу нажать на кнопку "📖 История транзакций".
'''