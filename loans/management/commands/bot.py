from datetime import timedelta
from functools import partial
from gettext import translation
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from users.models import User
from django.contrib.auth.models import User

from django.core.files.base import ContentFile
from io import BytesIO
from telegram import InputFile
from PIL import Image
import tempfile
import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import webbrowser
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from loans.models import User, Transaction

from telebot import TeleBot, types
from loans.models import TelegramMessageId, Contact, Transaction, Notification
from loans.bot.buttons import main_keyboard, detail_keyboard, start_keyboard, instruction_keyboard, edit_keyboard
from loans.bot.math import calculate_total
from loans.bot.expand import get_paginated_contacts, get_paginated_debit, get_paginated_credit
from loans.bot.text import my_profile, transaction_history, history, transaction_message, search_instr, add_contact_message, register_instr, add_contact_instr, history_instr
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import telebot
import re

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
import users
import os

User = get_user_model()

bot = TeleBot(settings.TELEGRAM_TOKEN, threaded=False)


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
    
    

def t_m_create(chat_id, message_id, action, contact_id):
    TelegramMessageId.objects.create(
        chat_id=chat_id,
        message_id=message_id,
        action=action,
        contact_id=contact_id
    )

def send_notification(chat_id, text):
    bot.send_message(
        chat_id=chat_id,
        text=text
    )

class Command(BaseCommand):
    help = 'MyCash'

    def handle(self, *args, **options):
        bot.remove_webhook()
        bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL)

@bot.message_handler(commands=['start', '/command1'])
def handle_command1(message):

    user_exists = User.objects.filter(chat_id=message.chat.id).exists()
    if not user_exists:
        instructions = '''
        Добро пожаловать в нашего бота!
        Инструкции по регистрации:
        1. Для регистрации нажмите на кнопку "Sign Up" и следуйте указаниям.
        2. Для входа в существующий аккаунт нажмите на кнопку "Login" и следуйте указаниям.
        3. После успешной регистрации или входа в систему вы сможете использовать кнопки меню для управления ботом.

        Для более подробных инструкций по использованию бота нажмите на /command1 после регистрации.
        '''
        image_url = 'https://cdn.pixabay.com/photo/2018/04/23/16/22/welcome-3344772_1280.jpg'
        bot.send_photo(chat_id=message.chat.id, photo=image_url)
        bot.send_message(message.chat.id, instructions, reply_markup=start_keyboard())
    else:
        
        user = User.objects.get(chat_id=message.chat.id)
        username = user.username.split(':')[0]
        image_url = 'https://img.freepik.com/free-photo/top-view-welcome-back-message-with-coffee-cup_23-2150462103.jpg?w=900&t=st=1688083434~exp=1688084034~hmac=9f84a0b1d4a222d567d8fc538cf81f070ddc5ebd64e31435513a59f695519ac3'
        bot.send_photo(chat_id=message.chat.id, photo=image_url)
        bot.send_message(message.chat.id, f'Вы уже зарегистрированы как {username}.', reply_markup=main_keyboard())
        
user_states = {}



def get_user_state(chat_id):
    return user_states.get(chat_id)

def set_user_state(chat_id, state):
    user_states[chat_id] = state

@bot.message_handler(func=lambda message: message.text == 'Sign Up')
def handle_sign_up(message):
    bot.send_message(message.chat.id, 'Введите свое имя пользователя и пароль в формате (имя пользователя:пароль) для регистрации')
    bot.register_next_step_handler(message, process_signup_step)

def process_signup_step(message):
    credentials = message.text.split(':')
    if len(credentials) != 2:
        bot.send_message(message.chat.id, 'Введите имя пользователя и пароль в правильном формате')
    else:
        username, password = credentials
        user = User(username=username, password=password, chat_id=message.chat.id)
        user.save()
        image_url1 = 'https://cdn.pixabay.com/photo/2014/04/20/12/30/thumb-328420_1280.jpg'  # Замените на фактический URL первой картинки
        bot.send_photo(chat_id=message.chat.id, photo=image_url1)
        bot.send_message(message.chat.id, f'Вы зарегистрированы как: {username}', reply_markup=main_keyboard())

STATE_LOGIN_START = 1
STATE_LOGIN_CREDENTIALS = 2

@bot.message_handler(func=lambda message: message.text == 'Login')
def login(message):
    if User.objects.filter(chat_id=message.chat.id).exists():
        user = User.objects.get(chat_id=message.chat.id)
        username = user.username.split(':')[0]
        image_url1 = 'https://cdn.pixabay.com/photo/2014/04/20/12/30/thumb-328420_1280.jpg'  # Замените на фактический URL первой картинки
        bot.send_photo(chat_id=message.chat.id, photo=image_url1)
        bot.send_message(message.chat.id, f'Вы уже вошли в систему как: {username}', reply_markup=main_keyboard())
    else:
        bot.send_message(
            message.chat.id,
            'Пожалуйста, введите свой имя пользователя и пароль в формате "Имя пользователя:Пароль" '
        )
        set_user_state(message.chat.id, STATE_LOGIN_START)

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == STATE_LOGIN_START)
def process_login(message):
    if ':' in message.text:
        set_user_state(message.chat.id, STATE_LOGIN_CREDENTIALS)
        handle_login_credentials(message)
    else:
        image_url1 = 'https://img.freepik.com/premium-vector/woman-with-pink-button-that-says-x_495252-122.jpg?w=1380'  # Замените на фактический URL первой картинки
        bot.send_photo(chat_id=message.chat.id, photo=image_url1)
        bot.send_message(
            message.chat.id,
            'Пожалуйста, введите никнейм и пароль в правильном формате.'
        )

def handle_login_credentials(message):
    credentials = message.text.split(':')
    username, password = credentials
    try:
        user = User.objects.get(username=username, password=password)
        user.chat_id = message.chat.id
        user.save()
        bot.send_message(message.chat.id, f'Вы успешно вошли как: {username}', reply_markup=main_keyboard())
        image_url1 = 'https://cdn.pixabay.com/photo/2014/04/20/12/30/thumb-328420_1280.jpg'  # Замените на фактический URL первой картинки
        bot.send_photo(chat_id=message.chat.id, photo=image_url1)
    except User.DoesNotExist:
        image_url1 = 'https://img.freepik.com/premium-vector/woman-with-pink-button-that-says-x_495252-122.jpg?w=1380'  # Замените на фактический URL первой картинки
        bot.send_photo(chat_id=message.chat.id, photo=image_url1)
        bot.send_message(message.chat.id, 'Неверный никнейм или пароль.')  

@bot.message_handler(func=lambda message: message.text == '/command2')
def logout(message):
    if User.objects.filter(chat_id=message.chat.id).exists():
        user = User.objects.get(chat_id=message.chat.id)
        user.chat_id = None
        user.save()
        bot.send_message(message.chat.id, 'Вы успешно вышли из системы.', reply_markup=start_keyboard())
        image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-DBvjvG__1EkWsUDW20DKEC-wo1Rdwq7BFUGMUwCh7pr3WBH_SlkNeStOf8NgpeJF-wQ&usqp=CAU'
        bot.send_photo(chat_id=message.chat.id, photo=image_url)
    else:
        bot.send_message(message.chat.id, 'Вы не авторизованы.', reply_markup=start_keyboard())

@bot.message_handler(func=lambda message: message.text == '/command1')
def handle_command1(message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
        instructions = '''Это Инструкция по использованию бота MyCash.\nНажмите на вопрос, который вас интересует, и мы выдадим вам подробную инструкцию использованию.'''
        keyboard = instruction_keyboard(user)
        image_url = 'https://img.freepik.com/premium-vector/black-man-filling-out-paperwork_112255-3004.jpg?w=1480'
        bot.send_photo(chat_id=message.chat.id, photo=image_url)
        bot.send_message(message.chat.id, instructions, reply_markup=keyboard)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, "Вы не авторизованы")

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
        contact = message.contact
        saved_contact = Contact.objects.create(
            name=contact.first_name,
            number=contact.phone_number,
            user=user
        )  
    

        keyboard = types.InlineKeyboardMarkup()
        borrow_button = types.InlineKeyboardButton(text='Дать займ', callback_data=f'{saved_contact.id}:borrow')
        lend_button = types.InlineKeyboardButton(text='Взять займ', callback_data=f'{saved_contact.id}:lend')
        keyboard.row(borrow_button, lend_button)          
        bot.send_message(message.chat.id, 'Создан новый контакт:')
        bot.send_photo(message.chat.id, caption=f'Имя: {saved_contact.name}\nНомер: {saved_contact.number}', reply_markup=keyboard)

    except User.DoesNotExist:
        bot.send_message(message.chat.id, "Вы не авторизованы")

 

@bot.message_handler()
def handle_message (message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
        if message.text == '💸 Новый займ':
            contacts, is_last, is_first = get_paginated_contacts(user.id, 0, 5)
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            for contact in contacts:
                contact_button = f'{contact.name}-{contact.number}'
                button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
                keyboard.add(button)
            expand_button = types.InlineKeyboardButton(text='>>>>', callback_data=f'{user.id}:expand-10')
            keyboard.row(expand_button)
            search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user.id}:search')
            keyboard.row(search_button)
            add_contact_button = types.InlineKeyboardButton (text='+ Контакт', callback_data=f'{user.id}:add_contact')
            keyboard.row(add_contact_button)
            bot.send_message(message.chat.id, 'Вы перешли в раздел Новый займ', reply_markup=keyboard)

        if message.text == '👤 Мой профиль':
            answer_message = my_profile(user.id)
            bot.send_message(message.chat.id, answer_message)
            keyboard = types.InlineKeyboardMarkup()
            debit_button = types.InlineKeyboardButton(text=f'Мне должны', callback_data=f'{user.id}:debit')
            keyboard.add(debit_button)
            credit_button = types.InlineKeyboardButton (text=f'Я должен', callback_data=f'{user.id}:credit')
            keyboard.add(credit_button)
            history_button = types.InlineKeyboardButton(text='📖 История транзакций', callback_data=f'{user.id}:transaction_history')
            keyboard.add(history_button)
            statistik_button = types.InlineKeyboardButton(text='📊  Статистика', callback_data=f'{user.id}:statistics')  
            keyboard.add(statistik_button)
            bot.send_message(message.chat.id, 'Дополнительные действия:', reply_markup=keyboard)
            

        if message.text == '🔍 Быстрый поиск':
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            debit_button = types.InlineKeyboardButton(text=f'Мне должны', callback_data=f'{user.id}:debit')
            keyboard.row(debit_button)
            credit_button = types.InlineKeyboardButton (text=f'Я должен', callback_data=f'{user.id}:credit')
            keyboard.row(credit_button)
            search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user.id}:search')
            keyboard.row(search_button)
            add_contact_button = types.InlineKeyboardButton (text='+ Контакт', callback_data=f'{user.id}:add_contact')
            keyboard.row(add_contact_button)
            bot.send_message(message.chat.id, 'Вы перешли в раздел 🔍 Быстрый поиск', reply_markup=keyboard)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, "Вы не авторизованы")
     



@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    callback_data = call.data.split(':')
    contact_id = callback_data[0]
    action = callback_data[1]
    user_id = call.message.chat.id
    print (call.data)

    if action == 'borrow':
        bot.send_message(call.message.chat.id, 'Введите сумму займа:')
        bot.register_next_step_handler(call.message, handle_amount_credit, contact_id, 'borrow', 'долг', 'credit')
    elif action == 'lend':
        bot.send_message(call.message.chat.id, 'Введите сумму долга:')
        bot.register_next_step_handler(call.message, handle_amount_credit, contact_id, 'lend', 'займ', 'debit')
    elif action == 'repay':
        bot.send_message(call.message.chat.id, 'Введите сумму погашения долга:')
        bot.register_next_step_handler(call.message, handle_amount_debit, contact_id, 'repay', 'погашение долга', 'credit')
    elif action == 'receive':
        bot.send_message(call.message.chat.id, 'Введите сумму получения займа:')
        bot.register_next_step_handler(call.message, handle_amount_debit, contact_id, 'receive', 'получение займа', 'debit')
    elif action == 'add_contact':
        bot.send_message(call.message.chat.id, 'Введите имя и номер контакта в формате (имя:номер)')
        bot.register_next_step_handler(call.message, create_contact, user_id)
    elif action == 'search':
        bot.send_message(call.message.chat.id, 'Введите имя или номер контакта для поиска')
        bot.register_next_step_handler(call.message, handle_search, contact_id, user_id)
    elif action == 'delete':
        image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYpbOyR8P-E6hrY_gfpMR0GXdy507ZRjXC_Zw8CbsHJg&s'
        bot.send_photo(chat_id=call.message.chat.id, photo=image_url)
        bot.send_message(call.message.chat.id, 'Вы уверены что хотите удалить контакт? Да/Нет".')
        bot.register_next_step_handler(call.message, confirm_delete_contact, contact_id)
    elif action == 'add_comment':
        bot.send_message(call.message.chat.id, 'Введите комментарий:')
        bot.register_next_step_handler(call.message, handle_add_comment, contact_id)
    elif action == 'edit_contact_name':
        bot.send_message(call.message.chat.id, 'Введите новое имя контакта:')
        bot.register_next_step_handler(call.message, edit_contact_name, contact_id)
    elif action == 'edit_contact_number':
        bot.send_message(call.message.chat.id, 'Введите новый номер контакта:')
        bot.register_next_step_handler(call.message, edit_contact_number, contact_id)
    
    elif 'detail' in call.data:
        contact_id, action = call.data.split(':')
        contact = Contact.objects.get(id=int(contact_id))
        keyboard = detail_keyboard(contact)
        history_button = types.InlineKeyboardButton("📖 История транзакций", callback_data=f"{contact_id}:history")
        keyboard.row(history_button)
        bot.send_message(call.message.chat.id, f'Контакт: {contact.name}\nНомер: {contact.number}\nМне должны: {contact.debit}\nЯ должен: {contact.credit}', reply_markup=keyboard)

    elif 'debit_expand' in call.data:
        user_id, action = call.data.split(':')
        contacts = Contact.objects.filter(user_id=user_id).exclude(debit=0).order_by('debit')
        page = int(action.split('-')[1])
        previous_page = max(0, page - 5)  # Вычисление номера предыдущей страницы
        next_page = page + 5
        contacts, is_last, is_first = get_paginated_debit(user_id, previous_page, 5)
        total_debit = calculate_total(user_id,'debit')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for contact in contacts:
            contact_button = f'{contact.name}-{contact.debit}'
            button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
            keyboard.add(button)
        
        if not is_first:
            previous_button = types.InlineKeyboardButton(text='<<<<', callback_data=f'{user_id}:debit_expand-{previous_page}')
            keyboard.row(previous_button)  
        if not is_last:
            expand_button = types.InlineKeyboardButton(text='>>>>', callback_data=f'{user_id}:debit_expand-{next_page}')
            keyboard.row(expand_button)
        
        search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user_id}:search')
        keyboard.row(search_button)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f'Вы перешли в раздел Мне должны\nОбщая сумма займов: {total_debit}', reply_markup=keyboard)

    elif 'credit_expand' in call.data:
        user_id, action = call.data.split(':')
        contacts = Contact.objects.filter(user_id=user_id).exclude(credit=0).order_by('credit')
        page = int(action.split('-')[1])
        previous_page = max(0, page - 5)  # Вычисление номера предыдущей страницы
        next_page = page + 5
        contacts, is_last, is_first = get_paginated_credit(user_id, previous_page, 5)
        total_credit = calculate_total(user_id,'credit')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for contact in contacts:
            contact_button = f'{contact.name}-{contact.credit}'
            button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
            keyboard.add(button)
        
        if not is_first:
            previous_button = types.InlineKeyboardButton(text='<<<<', callback_data=f'{user_id}:credit_expand-{previous_page}')
            keyboard.row(previous_button)  
        if not is_last:
            expand_button = types.InlineKeyboardButton(text='>>>>', callback_data=f'{user_id}:credit_expand-{next_page}')
            keyboard.row(expand_button)
        
        search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user_id}:search')
        keyboard.row(search_button)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f'Вы перешли в раздел Я должен\nОбщая сумма займов: {total_credit}', reply_markup=keyboard)

        if contact.photo:
                # Отправляем фотографию контакта вместе с текстом деталей
                photo_data = BytesIO(contact.photo.read())
                photo_data.seek(0)
                bot.send_photo(chat_id=call.message.chat.id, photo=photo_data, caption='Фотография контакта:')
       
        
         
        
    elif 'debit' in call.data:
        user_id, action = call.data.split(':')
        contacts = Contact.objects.filter(user_id=user_id).exclude(debit=0).order_by('debit')
        total_debit = calculate_total(user_id,'debit')
        contacts, is_last, is_first = get_paginated_debit(user_id, 0, 5)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for contact in contacts:
            contact_button = f'{contact.name}-{contact.debit}'
            button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
            keyboard.add(button)
        expand_button = types.InlineKeyboardButton(text='>>>>', callback_data=f'{user_id}:debit_expand-10')
        keyboard.row(expand_button)
        search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user_id}:search')
        keyboard.row(search_button)
        bot.send_message(call.message.chat.id, f'Вы перешли в раздел Мне должны\nОбщая сумма: {total_debit}', reply_markup=keyboard)
    elif 'credit' in call.data:
        user_id, action = call.data.split(':')
        contacts = Contact.objects.filter(user_id=user_id).exclude(credit=0).order_by('credit')
        contacts, is_last, is_first = get_paginated_credit(user_id, 0, 5)
        total_credit = calculate_total(user_id,'credit')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for contact in contacts:
            contact_button = f'{contact.name}-{contact.credit}'
            button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
            keyboard.add(button)
        expand_button = types.InlineKeyboardButton(text='>>>>', callback_data=f'{user_id}:credit_expand-10')
        keyboard.row(expand_button)
        search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user_id}:search')
        keyboard.row(search_button)
        bot.send_message(call.message.chat.id, f'Вы перешли в раздел Я должен\nОбщая сумма займов: {total_credit}', reply_markup=keyboard)
    elif 'transaction_history' in call.data:
        user_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = transaction_history(user_id)
        bot.send_message(chat_id=chat_id, text=message)

    
    
    elif 'history_instr' in call.data:
        contact_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = history_instr
        image_url = 'https://sputnik.kg/img/07e4/0c/17/1050869481_0:0:2752:1548_1920x0_80_0_0_68b6f91f5d1cf51ee72b3dbd722bba30.jpg'
        bot.send_photo(chat_id=chat_id, photo=image_url)
        bot.send_message(call.message.chat.id, text=message)
        
    elif 'history' in call.data:
        contact_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = history(contact_id)
        bot.send_message(call.message.chat.id, text=message)
    
    elif 'new_transaction_instr' in call.data:
        user_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = transaction_message
        image_url = 'https://vyborzayma.ru/wp-content/uploads/2017/05/tochkazaima_710-400.jpg'
        bot.send_photo(chat_id=chat_id, photo=image_url)
       
        bot.send_message(call.message.chat.id, text=message)
    elif 'add_contact_instr' in call.data:
        user_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = add_contact_instr
        image_url = 'https://tgrm-a.akamaihd.net/blog/wp-content/uploads/2018/09/kak-dobavit-kontakt-telegram-3.jpg'
        bot.send_photo(chat_id=chat_id, photo=image_url)
       
        bot.send_message(call.message.chat.id, text=message)

    elif 'add_contact' in call.data:
        answer_message = add_contact_message
        user_id, action = call.data.split(':')
        sent_message = bot.send_message(
            call.message.chat.id,
            answer_message)
        TelegramMessageId.objects.create(
            chat_id=call.message.chat.id,
            message_id=sent_message.message_id,
            action='add_contact',)
   
    elif 'register_instr' in call.data:
        user_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = register_instr
        image_url = 'https://partnerkin.com/storage/files/file_1659600957_3.webp'
        bot.send_photo(chat_id=chat_id, photo=image_url)
        bot.send_message(call.message.chat.id, text=message)

    elif 'search_instr' in call.data:
        user_id, action = call.data.split(':')
        chat_id = call.message.chat.id
        message = search_instr
        image_url = 'https://risovach.ru/upload/2013/05/mem/nelzya-prosto-tak-vzyat-i-boromir-mem_18337005_orig_.jpg'
        bot.send_photo(chat_id=chat_id, photo=image_url)
        bot.send_message(call.message.chat.id, text=message)
    
    elif 'search' in call.data:
        contact_id, action = call.data.split(':')
        sent_message = bot.send_message(
            call.message.chat.id,
            '''Напишите имя или номер контакта для поиска''')
        TelegramMessageId.objects.create(
            chat_id=call.message.chat.id,
            message_id=sent_message.message_id,
            action='search',
            )

    elif 'expand' in call.data:
        user_id, action = call.data.split(':')
        page = int(action.split('-')[1])
        previous_page = max(0, page - 5)  # Вычисление номера предыдущей страницы
        next_page = page + 5
        contacts, is_last, is_first = get_paginated_contacts(user_id, previous_page, 5)  # Получение контактов для предыдущей страницы
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for contact in contacts:
            contact_button = f'{contact.name}-{contact.number}'
            button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
            keyboard.add(button)
        
        if not is_first:
            previous_button = types.InlineKeyboardButton(text='<<<<', callback_data=f'{user_id}:expand-{previous_page}')
            keyboard.row(previous_button)  
        if not is_last:
            expand_button = types.InlineKeyboardButton(text='>>>>', callback_data=f'{user_id}:expand-{next_page}')
            keyboard.row(expand_button)
        
        search_button = types.InlineKeyboardButton(text='🔍 Поиск', callback_data=f'{user_id}:search')
        keyboard.row(search_button)
        add_contact_button = types.InlineKeyboardButton(text='+ Контакт', callback_data=f'{user_id}:add_contact')
        keyboard.row(add_contact_button)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Вы перешли в раздел 💸 Новый займ', reply_markup=keyboard)

    elif action == 'notification':
        bot.send_message(call.message.chat.id, 'Введите количество дней для срока погашения:')
        transaction_id = int(call.data.split(':')[0])
        callback = partial(handle_notification_callback, transaction_id=transaction_id)
        bot.register_next_step_handler(call.message, callback)
        print(2)    

    elif 'edit' in call.data:
        contact_id = call.data.split(':')[0]
        # Получите контакт из базы данных на основе contact_id
        contact = Contact.objects.get(id=int(contact_id))
        # Отправьте клавиатуру редактирования контакта
        keyboard = edit_keyboard(contact)
        bot.send_message(call.message.chat.id, 'Редактирование контакта', reply_markup=keyboard)  
    elif 'delete_photo' in call.data:
        contact_id, action = call.data.split(':')
        delete_photo(contact_id, call.message)     
    elif 'statistics' in call.data:
        statistic = get_statistics(call.message,user_id)  # Здесь вызывается функция get_statistics() для получения статистики
        if statistic:
            bot.send_message(call.message.chat.id, statistic)
        else:
            bot.send_message(call.message.chat.id, 'Вам была предоставлена информация о ваших пользователях')    

    elif 'add_photo' in call.data:
         bot.send_message(call.message.chat.id, 'Пришлите фотографию для сохранения')
         bot.register_next_step_handler(call.message, save_photo, contact_id)        

    
    

def handle_amount_credit(
        message, 
        contact_id, 
        transaction_type,
        transaction_desc,
        amount_field,
        transaction_id=None,
        error_count=0,
    ):
    try:  
        contact = Contact.objects.get(id=contact_id)
        amount = message.text
        if not amount.isnumeric():
            error_count += 1
            if error_count == 1:
                bot.send_message(
                    message.chat.id,
                    'Некорректное значение. Введите числовое значение.'
                )
                bot.register_next_step_handler(
                    message,
                    handle_amount_credit,
                    contact_id,
                    transaction_type,
                    transaction_desc,
                    amount_field,
                    transaction_id=transaction_id,
                    error_count=error_count
                )
            else:
                bot.send_message(
                    message.chat.id, 
                    'Вы ввели некорректное значение дважды. Попробуйте еще раз позже.'
                )
            return
        amount = int(amount)
        if transaction_id:
            transaction = Transaction.objects.get(id=transaction_id)
        else:
            transaction = Transaction.objects.create(
                transaction_type=transaction_type,
                contact=contact,
                amount=amount
            )
        setattr(contact, amount_field, amount)
        contact.save()
        if transaction_type == 'borrow':
            contact.credit += amount
        elif transaction_type == 'lend':
            contact.debit += amount
        total_amount = getattr(contact, amount_field)
        keyboard = types.InlineKeyboardMarkup()
        notification_button = types.InlineKeyboardButton("⌛️ Добавить срок погашения", 
                                                         callback_data=f"{transaction.id}:notification")
        keyboard.row(notification_button)
        history_button = types.InlineKeyboardButton("📖 История транзакций", 
                                                    callback_data=f"{contact_id}:history")
        keyboard.row(history_button)
        comment = types.InlineKeyboardButton(text=' 💬 Добавить комментарий', callback_data=f'{transaction.id}:add_comment')
        keyboard.add(comment)
        bot.send_message(
            message.chat.id,
            f'''Вы увеличили {transaction_desc} 
            \nКонтакта: {contact.name}
            \nНа сумму: {amount} сом
            \nОбщая сумма: {amount} сом''',
            reply_markup=keyboard
        )
    except Exception as e:
        print(str(e))
        bot.send_message(
            message.chat.id, 
            "Произошла ошибка. Попробуйте еще раз позже."
            )

def handle_notification_callback(message, transaction_id):
    try:
        repayment_days = int(message.text)

        transaction = Transaction.objects.get(id=transaction_id)
        repayment_date = transaction.created + timedelta(days=repayment_days)

        repayment_date_str = repayment_date.strftime("%Y.%m.%d %H:%M")

        notification = Notification(transaction=transaction, repayment_date=repayment_date)
        notification.save()

        bot.send_message(
            message.chat.id, 
            f"Создано уведомление о погашении транзакции до {repayment_date_str}."
            )
    except Transaction.DoesNotExist:
        bot.send_message(
            message.chat.id, 
            "Транзакция не найдена."
            )
    except Exception as e:
        print(str(e))
        bot.send_message(
            message.chat.id, 
            "Произошла ошибка. Попробуйте еще раз позже."
            )
def handle_amount_debit(message, contact_id, transaction_type, transaction_desc, amount_field):
    contact = Contact.objects.get(id=contact_id)
    amount = message.text
    if amount.isdigit():
        amount = int(amount)
    else:
        bot.send_message(message.chat.id, 'Некорректное значение. Введите числовое значение.')
        return

    if transaction_type == 'repay':
        if amount > contact.credit:
            excess_amount = amount - contact.credit
            Transaction.objects.create(transaction_type=transaction_type, contact=contact, amount=contact.credit)
            contact.credit = 0
            contact.debit += excess_amount 
            current_total = getattr(contact, amount_field)
            new_total = current_total - amount
        else:
            Transaction.objects.create(transaction_type=transaction_type, contact=contact, amount=amount)
            contact.credit -= amount
    elif transaction_type == 'receive':
        if amount > contact.debit:
            excess_amount = amount - contact.debit
            Transaction.objects.create(transaction_type=transaction_type, contact=contact, amount=contact.debit)
            contact.debit = 0
            contact.credit += excess_amount
            current_total = getattr(contact, amount_field)
            new_total = current_total - amount
        else:
            Transaction.objects.create(transaction_type=transaction_type, contact=contact, amount=amount)
            contact.debit -= amount
    contact.save()
    keyboard = types.InlineKeyboardMarkup()
    history_button = types.InlineKeyboardButton("📖 История транзакций", callback_data=f"{contact_id}:history")
    keyboard.row(history_button)
    image_url1 = 'https://cdn.pixabay.com/photo/2018/01/19/07/57/shaking-hands-3091906_1280.jpg'  # Замените на фактический URL первой картинки
    bot.send_photo(chat_id=message.chat.id, photo=image_url1)
       
    bot.send_message(message.chat.id,f'Вы уменьшили {transaction_desc} контакта: {contact.name}\nна сумму: {amount} сом\n\nОбщая сумма: {getattr(contact, amount_field)} сом',reply_markup=keyboard)

def create_contact(message, user_id):
    name, number = message.text.split(':')
    if not (number.startswith('+') or number.startswith('0')):
        bot.send_message(message.chat.id, 'Неверный указан номер телефона.')
        sent_message = bot.send_message(message.chat.id, 'Номер телефона должен начинаться с "0" или "+", если нужно указать код страны. Повторите попытку:')
        bot.register_next_step_handler(sent_message, create_contact, user_id)  # Рекурсивный вызов функции
        return
    if number.startswith('+'):
        number = number[1:]
    try:
        user = User.objects.get(chat_id=user_id)
        contact = Contact.objects.create(name=name, number=number, user=user)
        keyboard = types.InlineKeyboardMarkup()
        borrow_button = types.InlineKeyboardButton(text='Дать займ', callback_data=f'{contact.id}:borrow')
        lend_button = types.InlineKeyboardButton(text='Взять займ', callback_data=f'{contact.id}:lend')
        keyboard.row(borrow_button, lend_button)
        bot.send_message(message.chat.id, 'Создан новый контакт:')
        bot.send_message(message.chat.id, f'Имя: {contact.name}\nНомер: {contact.number}', reply_markup=keyboard)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, "Вы не авторизованы")

def handle_search(message, contact_id, user_id):
    search_query = message.text.strip()
    try:
        user = User.objects.get(chat_id=user_id)
        contacts = Contact.objects.filter(user=user).filter(
            Q(name__icontains=search_query) | Q(number__icontains=search_query))
        if contacts.exists():
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for contact in contacts:
                contact_button = f'{contact.name} - {contact.number}'
                button = types.InlineKeyboardButton(text=contact_button, callback_data=f"{contact.id}:detail")
                keyboard.add(button)
            bot.send_message(message.chat.id, 'Результаты поиска:', reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            add_contact_button = types.InlineKeyboardButton(text='+ Контакт', callback_data=f'{user_id}:add_contact')
            keyboard.row(add_contact_button)
            image_url = 'https://img.freepik.com/premium-vector/thinking-woman-thoughtful-pensive-making-decision-young-female-character-flat-vector-illustration-thinking-cartoon-lady_519741-127.jpg?w=1380'
            bot.send_photo(chat_id=message.chat.id, photo=image_url)
            bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.', reply_markup=keyboard)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, "Вы не авторизованы")
    


def edit_contact_name(message, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
        contact.name = message.text
        contact.save()
        bot.send_message(message.chat.id, f'Имя контакта успешно изменено на "{contact.name}".')
    except Contact.DoesNotExist:
        bot.send_message(message.chat.id, 'Контакт не найден.')

def cancel_delete_contact(message):
    # Отмена удаления контакта
    user_id = message.from_user.id
    bot.send_message(chat_id=user_id, text='Удаление контакта отменено.')

def confirm_delete_contact(message, contact_id):
    contact = Contact.objects.get(id=contact_id)
    user_id = message.from_user.id
    
    if message.text.lower() in ['отмена', 'нет', 'no']:
        cancel_delete_contact(message)
    elif message.text.lower() in ['удалить', 'да', 'yes']:
        if contact.debit > 0 or contact.credit > 0:
            bot.send_message(chat_id=user_id, text='У контакта есть не закрытые транзакции. Нельзя удалить контакт.')
        else:
            # Код для удаления контакта
            contact.delete()
            bot.send_message(chat_id=user_id, text='Контакт успешно удален.')
    else:
        bot.send_message(chat_id=user_id, text='Пожалуйста, отправьте "Да/Yes" или "Нет/No" для подтверждения действия.')


def edit_contact_number(message, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
        contact.number = message.text
        contact.save()
        bot.send_message(message.chat.id, f'Номер контакта успешно изменен на "{contact.number}".')
    except Contact.DoesNotExist:
        bot.send_message(message.chat.id, 'Контакт не найден.')

def handle_add_comment(message, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    comment = message.text
    transaction.comment = comment
    print(transaction)
    transaction.save()
    print(transaction)
    bot.send_message(message.chat.id, 'Вы добавили комментарий')   

@bot.message_handler(commands=['statistics'])
def get_statistics(message, user_id):
    total_contacts=Contact.objects.filter(user__chat_id=user_id).count()
    total_transactions = Transaction.objects.filter(contact__user__chat_id=user_id).count()
    total_transaction_amount = Transaction.objects.filter(contact__user__chat_id=user_id).aggregate(total_amount=Sum('amount'))['total_amount']
    
    if total_transaction_amount is None:
        total_transaction_amount = 0

    
    information_text = f'''
                      Статистика:
    Общее количество контактов:  {total_contacts}
    Количество успешных транзакций: {total_transactions}
    Общая сумма всех транзакций всех пользователей:{round(total_transaction_amount, 2)}
    '''
    bot.send_message(chat_id=message.chat.id, text=information_text)
    image_url = 'https://img.freepik.com/free-photo/top-view-of-statistics-presentation-with-pie-chart_23-2149023802.jpg?w=2000&t=st=1688997456~exp=1688998056~hmac=1a80aef4bb4ed117b964c5f7ba275ea04e6607472c705be2505637cf27248cab'
    bot.send_photo(chat_id=message.chat.id, photo=image_url)



def save_photo(message, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
        photo = message.photo[-1]  # Получаем последнюю отправленную фотографию
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Сохраняем фотографию на сервере
        file_extension = file_info.file_path.split('.')[-1]
        photo_path = f'contact_photos/{contact_id}.{file_extension}'
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        # Сохраняем путь к фотографии в модели Contact
        contact.photo = photo_path
        contact.save()
        bot.send_message(message.chat.id, 'Фотография успешно сохранена')
    except Contact.DoesNotExist:
        bot.send_message(message.chat.id, 'Контакт не найден')

def delete_photo(contact_id, message):
    try:
        contact = Contact.objects.get(id=contact_id)
        if contact.photo:
            # Удаляем файл фотографии с диска
            photo_path = contact.photo.path
            os.remove(photo_path)
            # Сбрасываем поле фотографии в модели Contact
            contact.photo = None
            contact.save()
            bot.send_message(message.chat.id, 'Фотография успешно удалена')
        else:
            bot.send_message(message.chat.id, 'Фотография не найдена')
    except Contact.DoesNotExist:
        bot.send_message(message.chat.id, 'Контакт не найден')        






def save_photo(message, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
        photo = message.photo[-1]  # Получаем последнюю отправленную фотографию
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Сохраняем фотографию на сервере
        file_extension = file_info.file_path.split('.')[-1]
        photo_path = f'contact_photos/{contact_id}.{file_extension}'
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        # Сохраняем путь к фотографии в модели Contact
        contact.photo = photo_path
        contact.save()
        bot.send_message(message.chat.id, 'Фотография успешно сохранена')
    except Contact.DoesNotExist:
        bot.send_message(message.chat.id, 'Контакт не найден')

def delete_photo(contact_id, message):
    try:
        contact = Contact.objects.get(id=contact_id)
        if contact.photo:
            # Удаляем файл фотографии с диска
            photo_path = contact.photo.path
            os.remove(photo_path)
            # Сбрасываем поле фотографии в модели Contact
            contact.photo = None
            contact.save()
            bot.send_message(message.chat.id, 'Фотография успешно удалена')
        else:
            bot.send_message(message.chat.id, 'Фотография не найдена')
    except Contact.DoesNotExist:
        bot.send_message(message.chat.id, 'Контакт не найден')        






    
