import sqlite3
import re
from datetime import datetime
from config import bot
from telebot import types
from markup import menu_markup



def get_name(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''
    name = first_name + (' ' + last_name if last_name else '')
    bot.send_message(message.chat.id, f'👋Привет {name}\n'
                                    'Я твой профессиональный 🎴нейро-таролог') 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = types.KeyboardButton('Да')
    markup.add(btn_yes)
    bot.send_message(message.chat.id, 'Для начала давай познакомимся немного поближе. \n'
                                    f'{name} это твое настоящее имя? \n\n'
                                    'Если ДА, нажми на кнопку "Да", если НЕТ, напиши мне свое настоящее имя.', reply_markup=markup)  
    bot.register_next_step_handler(message, ask_birth_date) 


def ask_birth_date(message):
    if message.text != 'Да' and message.text != 'да' and message.text != 'ДА':
        name = message.text
    else:
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name or ''
        name = first_name + (' ' + last_name if last_name else '')

    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f'Приятно познакомиться, {name}!\n\n'
                                    'Теперь, пожалуйста, напиши мне свою дату рождения в формате ДД.ММ.ГГГГ (например, 25.12.1990).', reply_markup=markup)  
    bot.register_next_step_handler(message, save_user_info, name) 


def save_user_info(message, name):
    birth_date = message.text.strip()
    
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(date_pattern, birth_date):
        bot.send_message(message.chat.id, '❌ Неверный формат даты!\n\n'
                                        'Пожалуйста, введи дату рождения в формате ДД.ММ.ГГГГ\n'
                                        'Например: 25.12.1990')
        bot.register_next_step_handler(message, save_user_info, name)
        return
    
    try:
        day, month, year = birth_date.split('.')
        date_obj = datetime(int(year), int(month), int(day))
        
        if date_obj > datetime.now():
            bot.send_message(message.chat.id, '❌ Дата рождения не может быть в будущем!\n\n'
                                            'Пожалуйста, введи корректную дату рождения в формате ДД.ММ.ГГГГ')
            bot.register_next_step_handler(message, save_user_info, name)
            return
            
    except ValueError:
        bot.send_message(message.chat.id, '❌ Такой даты не существует!\n\n'
                                        'Пожалуйста, введи корректную дату рождения в формате ДД.ММ.ГГГГ\n'
                                        'Например: 25.12.1990')
        bot.register_next_step_handler(message, save_user_info, name)
        return
    
    try:
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else ''
        telegram_name = message.from_user.first_name + ' ' + (message.from_user.last_name or '')
        
        conn = sqlite3.connect('baza.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO conversations (user_id, username, name, real_name, birth_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, telegram_name, name, birth_date))
        
        conn.commit()
        conn.close()
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_restart_reg = types.InlineKeyboardButton('Я хочу начать заново', callback_data='restart_reg')
        btn_ok_reg = types.InlineKeyboardButton('✅Все верно', callback_data='ok_reg')
        markup.add(btn_restart_reg, btn_ok_reg)

        bot.send_message(message.chat.id, 'Верно ли я сохранил твои данные?\n\n' \
                                    f'Имя: {name}\n'
                                    f'Дата рождения: {birth_date}\n\n', reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при сохранении данных. Пожалуйста, попробуйте еще раз.') 
        print(f"Ошибка в save_user_info: {e} \n"
            "Обратись к разработчкику @DurnovP")


@bot.callback_query_handler(func=lambda call: call.data in ['restart_reg', 'ok_reg'])
def handle_registration_confirmation(callback):
    if callback.data == 'restart_reg':
        bot.edit_message_text("🔃Начинаем регистрацию заново.", callback.message.chat.id, callback.message.message_id, reply_markup=None)
        get_name(callback.message)
    elif callback.data == 'ok_reg':
        bot.edit_message_text('Спасибо! Твои данные сохранены успешно. 🎉', callback.message.chat.id, callback.message.message_id, reply_markup=None)
        bot.send_message(callback.message.chat.id, 'Ну давай начнем🚀 \n\n'
                                                    'У тебя есть две кнопки, 🌟Подписка и 🎴Меню \n' \
                                                    '1) 🌟Подпиcка - чтоб получать расклады, нужно приобрести подписку\n'
                                                    '2) 🎴Меню - выбрать интересующий расклад или функцию', reply_markup=menu_markup())