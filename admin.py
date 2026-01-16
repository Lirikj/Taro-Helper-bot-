import sqlite3
from config import bot, developer
from telebot import types
from premium import activate_premium


def is_admin(user_id):
    return user_id == developer


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, '❌ У тебя нет доступа к админ панели.')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('👥 Список пользователей', callback_data='admin_users')
    btn2 = types.InlineKeyboardButton('📢 Рассылка всем', callback_data='admin_broadcast')
    btn3 = types.InlineKeyboardButton('✉️ Написать пользователю', callback_data='admin_message')
    btn4 = types.InlineKeyboardButton('⭐ Выдать себе подписку', callback_data='admin_give_self')
    btn5 = types.InlineKeyboardButton('🎁 Подарить подписку', callback_data='admin_gift')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(message.chat.id, '🔐 Админ панель:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback_handler(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, '❌ Нет доступа')
        return
    
    if call.data == 'admin_users':
        show_users_list(call)
    elif call.data == 'admin_broadcast':
        bot.edit_message_text('📢 Отправь сообщение для рассылки всем пользователям:', call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, broadcast_message)
    elif call.data == 'admin_message':
        bot.edit_message_text('✉️ Отправь в формате:\n'
                            'user_id текст сообщения\n\n'
                            'Пример:\n123456789 Привет!', call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, send_to_user)
    elif call.data == 'admin_give_self':
        bot.edit_message_text('⭐ Сколько дней подписки выдать себе?\n\n'
                            'Отправь число:', call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, give_self_premium)
    elif call.data == 'admin_gift':
        bot.edit_message_text('🎁 Отправь в формате:\n' 
                            'user_id количество_дней\n\n' 
                            'Пример:\n123456789 30', call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, gift_premium)
    
    bot.answer_callback_query(call.id)


def show_users_list(call):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, name, real_name FROM conversations')
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        bot.edit_message_text('📭 Пользователей пока нет.', call.message.chat.id, call.message.message_id)
        return
    
    text = f'👥 Всего пользователей: {len(users)}\n\n'
    
    for user_id, username, name, real_name in users:
        display_name = name if name else f'ID: {user_id}'
        username_text = f'@{username}' if username else 'нет username'
        real_name_text = f'({real_name})' if real_name else ''
        
        text += f'• {display_name} {real_name_text}\n'
        text += f'  {username_text}\n'
        text += f'  ID: {user_id}\n\n'
        
        if len(text) > 3500:
            bot.send_message(call.message.chat.id, text)
            text = ''
    
    if text:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)


def broadcast_message(message):
    if not is_admin(message.from_user.id):
        return
    
    broadcast_text = message.text
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM conversations')
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    fail_count = 0
    
    bot.send_message(message.chat.id, f'📢 Начинаю рассылку {len(users)} пользователям...')
    
    for (user_id,) in users:
        try:
            bot.send_message(user_id, broadcast_text)
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f'Не удалось отправить {user_id}: {e}')
    
    bot.send_message(message.chat.id, f'✅ Рассылка завершена!\n\n'
                                    f'Успешно: {success_count}\n'
                                    f'Ошибок: {fail_count}')


def send_to_user(message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, '❌ Неверный формат. Используй:\nuser_id текст')
            return
        
        user_id = int(parts[0])
        text = parts[1]
        
        bot.send_message(user_id, text)
        bot.send_message(message.chat.id, f'✅ Сообщение отправлено пользователю {user_id}')
    except ValueError:
        bot.send_message(message.chat.id, '❌ Неверный user_id')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка: {e}')


def give_self_premium(message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        days = int(message.text)
        months = days / 30
        
        expiry_date = activate_premium(message.from_user.id, f'Админ {days} дней', months)
        
        bot.send_message(message.chat.id, f'✅ Подписка активирована!\n\n'
                                        f'📅 Действует до: {expiry_date.strftime("%d.%m.%Y")}\n'
                                        f'⏰ Дней: {days}')
    except ValueError:
        bot.send_message(message.chat.id, '❌ Введи корректное число дней')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка: {e}')


def gift_premium(message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, '❌ Неверный формат. Используй:\nuser_id количество_дней')
            return
        
        user_id = int(parts[0])
        days = int(parts[1])
        months = days / 30
        
        expiry_date = activate_premium(user_id, f'Подарок {days} дней', months)
        
        bot.send_message(message.chat.id, f'✅ Подписка подарена пользователю {user_id}!\n\n'
                                        f'📅 Действует до: {expiry_date.strftime("%d.%m.%Y")}\n'
                                        f'⏰ Дней: {days}')
        
        try:
            bot.send_message(user_id, f'🎁 Тебе подарена премиум подписка!\n\n'
                                    f'⏰ Срок: {days} дней\n'
                                    f'📅 Действует до: {expiry_date.strftime("%d.%m.%Y")}\n\n'
                                    f'✨ Наслаждайся всеми возможностями бота!')
        except:
            pass
            
    except ValueError:
        bot.send_message(message.chat.id, '❌ Введи корректные данные')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка: {e}')
