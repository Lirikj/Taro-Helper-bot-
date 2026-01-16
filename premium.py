import sqlite3
from datetime import datetime, timedelta
from config import bot
from telebot import types
from markup import menu_markup


def get_premium_status(user_id):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    cursor.execute('SELECT premium_status, premium_expiry FROM premium WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False, None
    
    status, expiry = result
    if status == 'active' and expiry:
        expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
        if expiry_date > datetime.now():
            return True, expiry_date
        else:
            deactivate_premium(user_id)
            return False, None
    return False, None


def activate_premium(user_id, premium_type, months):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    cursor.execute('SELECT premium_expiry FROM premium WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if result and result[0]:
        current_expiry = datetime.strptime(result[0], '%Y-%m-%d')
        if current_expiry > datetime.now():
            new_expiry = current_expiry + timedelta(days=30 * months)
        else:
            new_expiry = datetime.now() + timedelta(days=30 * months)
    else:
        new_expiry = datetime.now() + timedelta(days=30 * months)
    
    cursor.execute('''
        INSERT OR REPLACE INTO premium (user_id, premium_type, premium_status, premium_expiry)
        VALUES (?, ?, 'active', ?)
    ''', (user_id, premium_type, new_expiry.strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    return new_expiry


def deactivate_premium(user_id):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE premium SET premium_status = "inactive" WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


def show_premium_menu(message):
    user_id = message.from_user.id
    is_premium, expiry_date = get_premium_status(user_id)
    
    if is_premium:
        days_left = (expiry_date - datetime.now()).days
        
        conn = sqlite3.connect('baza.db')
        cursor = conn.cursor()
        cursor.execute('SELECT premium_type FROM premium WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        premium_type = result[0] if result else 'Стандарт'
        
        text = f'✨У тебя активна премиум подписка!\n\n'
        text += f'📦Тариф: {premium_type}\n'
        text += f'📅Действует до: {expiry_date.strftime("%d.%m.%Y")}\n'
        text += f'⏰Осталось дней: {days_left}\n\n'
        text += '🎁Твои преимущества:\n'
        text += '✅Безлимитные вопросы Таро\n'
        text += '✅Безлимитные расклады\n'
        text += '✅Полная матрица судьбы\n'
        text += '✅Проверка совместимости\n\n'
        
        if days_left <= 7:
            text += f'⚠️Подписка заканчивается через {days_left} дней!\n'
        
        text += 'Хочешь продлить подписку?'
        
        bot.send_message(message.chat.id, text, reply_markup=premium_markup())
    else:
        bot.send_message(message.chat.id, '🌟Премиум подписка открывает:\n\n'
                                        '✅Безлимитные расклады\n'
                                        '✅Безлимитные вопросы\n'
                                        '✅Подробная матрица судьбы\n'
                                        '✅Расширенная совместимость\n'
                                        '✅Персональные рекомендации\n'
                                        '💎Выбери тариф:', reply_markup=premium_markup())


def premium_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('1 месяц - 99⭐', callback_data='premium_1')
    btn2 = types.InlineKeyboardButton('3 месяца - 199⭐', callback_data='premium_3')
    btn3 = types.InlineKeyboardButton('6 месяцев - 499⭐', callback_data='premium_6')
    btn4 = types.InlineKeyboardButton('1 год - 999⭐', callback_data='premium_12')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('premium_'))
def handle_premium_purchase(call):
    user_id = call.from_user.id
    premium_plans = {
        'premium_1': (1, 99, '1 месяц'),
        'premium_3': (3, 199, '3 месяца'),
        'premium_6': (6, 499, '6 месяцев'),
        'premium_12': (12, 999, '1 год')
    }
    
    if call.data in premium_plans:
        months, price, plan_name = premium_plans[call.data]
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f'Премиум подписка - {plan_name}',
            description=f'Премиум подписка на {plan_name}. Безлимитные расклады, матрица судьбы и многое другое!',
            invoice_payload=f'premium_{months}_{user_id}',
            provider_token='',
            currency='XTR',
            prices=[types.LabeledPrice(label=f'Подписка на {plan_name}', amount=price)],
            start_parameter=f'premium-{months}'
        )
    bot.answer_callback_query(call.id)


@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payload = message.successful_payment.invoice_payload
    parts = payload.split('_')
    months = int(parts[1])
    user_id = int(parts[2])
    premium_types = {1: '1 месяц', 3: '3 месяца', 6: '6 месяцев', 12: '1 год'}
    premium_type = premium_types.get(months, f'{months} месяцев')
    expiry_date = activate_premium(user_id, premium_type, months)
    
    bot.send_message(message.chat.id, f'🎉Поздравляю! Премиум подписка успешно активирована!\n\n'
                                    f'📦Тариф: {premium_type}\n'
                                    f'📅Действует до: {expiry_date.strftime("%d.%m.%Y")}\n\n'
                                    f'✨Теперь тебе доступны все возможности бота!', reply_markup=menu_markup())
