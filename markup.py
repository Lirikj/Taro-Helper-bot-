from telebot import types   


def get_premium():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('Оформить 🌟Премиум', callback_data='premium_1')
    markup.add(btn1)
    return markup


def menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🌟Подписка') 
    btn2 = types.KeyboardButton('🎴Меню')
    markup.add(btn1, btn2)
    return markup 


def spread_markup():
    markup = types.InlineKeyboardMarkup() 
    btn1 = types.InlineKeyboardButton('🌞Расклад', callback_data='spread_btn')
    btn2 = types.InlineKeyboardButton('❓Задать вопрос', callback_data='question_btn')
    btn3 = types.InlineKeyboardButton('🪞Матрица судьбы', callback_data='matrix_btn') 
    btn4 = types.InlineKeyboardButton('💑Проверка совместимости', callback_data='love_btn') 
    btn5 = types.InlineKeyboardButton('💔Расклад на отношения', callback_data='relationships_btn')
    btn6 = types.InlineKeyboardButton('🧠Карта состояния', callback_data='state_card_btn')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)            
    markup.add(btn4)
    markup.add(btn5)
    markup.add(btn6)
    return markup


def who_markup():
    markup = types.InlineKeyboardMarkup() 
    btn1 = types.InlineKeyboardButton('💆‍♀️Для себя', callback_data='for_self')
    btn2 = types.InlineKeyboardButton('🤝Для другого человека', callback_data='for_other') 
    markup.add(btn1, btn2)
    return markup


def type_date_markup():
    markup = types.InlineKeyboardMarkup() 
    btn1 = types.InlineKeyboardButton('На день', callback_data='date_day')
    btn2 = types.InlineKeyboardButton('На неделю', callback_data='date_week')
    btn3 = types.InlineKeyboardButton('На месяц', callback_data='date_month') 
    btn4 = types.InlineKeyboardButton('На год', callback_data='date_year') 
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup 


