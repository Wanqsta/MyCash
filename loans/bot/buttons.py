from telebot import TeleBot, types

def start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Sign Up')
    button2 = types.KeyboardButton('Login')
    keyboard.add(button1, button2)
    return keyboard

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('💸 Новый займ')
    button2 = types.KeyboardButton ('🔍 Быстрый поиск')
    button3 = types.KeyboardButton ('👤 Мой профиль')
    keyboard.add(button1, button2, button3)
    return keyboard


def detail_keyboard(contact):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    borrow = types.InlineKeyboardButton(text='Взять займ', callback_data=f'{contact.id}:borrow')
    repay = types.InlineKeyboardButton(text='Вернуть займ', callback_data=f'{contact.id}:repay')
    lend = types.InlineKeyboardButton(text='Дать займ', callback_data=f'{contact.id}:lend')
    receive = types.InlineKeyboardButton(text='Принять погащение', callback_data=f'{contact.id}:receive')
    edit_keyboard = types.InlineKeyboardButton(text='🖋Редактировать контакт', callback_data=f'{contact.id}:edit')
    add_photo_button = types.InlineKeyboardButton(text='Добавить фото', callback_data=f'{contact.id}:add_photo')
    keyboard.add(add_photo_button)
    keyboard.add(lend, receive)
    keyboard.add(borrow, repay)
    keyboard.add(edit_keyboard)
    return keyboard

def instruction_keyboard(user):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    register_button = types.InlineKeyboardButton(text='Как зарегистрироваться или сменить 👤 аккаунт?', callback_data=f'{user.id}:register_instr')
    transaction_button = types.InlineKeyboardButton(text='Как создать 💸 Новый займ?', callback_data=f'{user.id}:new_transaction_instr')
    add_contact_button = types.InlineKeyboardButton(text='Как добавить + Контакт?', callback_data=f'{user.id}:add_contact_instr')
    search_button = types.InlineKeyboardButton(text='Для чего нужна кнопка 🔍 Быстрый поиск?', callback_data=f'{user.id}:search_instr')
    history_button = types.InlineKeyboardButton(text='Что такое 📖 История транзакций?', callback_data=f'{user.id}:history_instr')
    keyboard.add(transaction_button, add_contact_button, register_button, search_button, history_button)
    return keyboard

def edit_keyboard(contact):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    delete = types.InlineKeyboardButton(text='❌ Удалить контакт', callback_data=f'{contact.id}:delete')
    edit_name = types.InlineKeyboardButton(text='📝 Изменить имя контакта', callback_data=f'{contact.id}:edit_contact_name')
    edit_number = types.InlineKeyboardButton(text='✏️ Изменить номер контакта', callback_data=f'{contact.id}:edit_contact_number')
    delete_photo = types.InlineKeyboardButton(text=' Удалить фото контакта', callback_data=f'{contact.id}:delete_photo')
    keyboard.add(delete_photo)
    keyboard.add(delete)
    keyboard.add(edit_name)
    keyboard.add(edit_number)
    return keyboard

