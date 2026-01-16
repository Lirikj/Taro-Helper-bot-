import random 
from config import bot 
from baza import has_premium, get_user_data
from chatGPT import chat_with_gpt
from markup import get_premium, type_date_markup


textz = [
    "🃏 Смотрю, как складывается ситуация…", 
    "🔮 Гадаю на картах Таро…",
    "🌙 Проясняется общий фон происходящего…", 
    "🌿 Становится понятнее, что сейчас влияет сильнее всего…", 
    "🔮 Ответ постепенно проявляется…", 
    "❤️ Проясняется эмоциональная сторона ситуации…", 
    "⚖️ Анализирую баланс сил в ситуации…",
    "🌟 Карты показывают возможные пути развития…",
    "🌀 Погружаюсь в глубины подсознания…",
    "✨ Карты Таро раскрывают свои тайны...",
    "🌞 Общий смысл периода начинает выстраиваться…"
]

@bot.callback_query_handler(func=lambda call: call.data in ['spread_btn', 'question_btn', 'matrix_btn', 'love_btn', 'relationships_btn', 'state_card_btn']) 
def handle_spread_request(call):
    if not has_premium(call.from_user.id):
        bot.edit_message_text('К сожалению у тебя отсутствует подписка.', call.message.chat.id, call.message.message_id, reply_markup=get_premium())
        return 
    
    if call.data == 'spread_btn':
        bot.edit_message_text('Выбери тип расклада:', call.message.chat.id, call.message.message_id, reply_markup=type_date_markup())
    elif call.data == 'question_btn':
        bot.edit_message_text('❓Задай свой вопрос:', call.message.chat.id,call.message.message_id)
        bot.register_next_step_handler(call.message, question)
    elif call.data == 'matrix_btn':
        bot.edit_message_text('⚡️Генерирую матрицу судьбы...', call.message.chat.id, call.message.message_id)
        generate_matrix(call)
    elif call.data == 'love_btn':
        bot.edit_message_text('💑Проверка совместимости:\n\n' 
                            'Напиши имя человека и дату его рождения, с которым хочешь проверить совместимость\n'
                            'Пример: Иван 15.08.1990',
                            call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, love)
    elif call.data == 'relationships_btn':
        bot.edit_message_text('💔Расклад на отношения\n\n'
                            'Опиши текущую ситуацию в отношениях:',
                            call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, relationships)
    elif call.data == 'state_card_btn':
        bot.edit_message_text(textz[random.randint(0, len(textz)-1)], call.message.chat.id, call.message.message_id)
        generate_state_card(call)
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data in ['date_day', 'date_week', 'date_month', 'date_year'])
def spread_date_handler(callback):
    from baza import get_user_data
    
    date_types = {
        'date_day': ('день', '🌞Расклад на день'),
        'date_week': ('неделю', '📅Расклад на неделю'),
        'date_month': ('месяц', '🌙Расклад на месяц'),
        'date_year': ('год', '✨Расклад на год')
    }
    
    if callback.data in date_types:
        period, title = date_types[callback.data]
        bot.edit_message_text(textz[random.randint(0, len(textz)-1)], callback.message.chat.id, callback.message.message_id)
        
        user_data = get_user_data(callback.from_user.id)
        
        prompt = f'Нужно сгенерировать расклад Таро на {period}. '
        if user_data:
            prompt += f'Для человека с именем {user_data["real_name"]}, дата рождения: {user_data["birth_date"]}. '
        prompt += 'Используй классический расклад из 3 карт: прошлое, настоящее, будущее. '
        prompt += 'Выбери 3 случайные карты Таро и сделай их интерпретацию.'
        
        result = chat_with_gpt(prompt)
        
        bot.edit_message_text(f'{title}\n\n{result}', callback.message.chat.id, callback.message.message_id, parse_mode='HTML')
    
    bot.answer_callback_query(callback.id)

def question(message):
    
    user_question = message.text
    user_data = get_user_data(message.from_user.id)
    
    sent_msg = bot.send_message(message.chat.id, textz[random.randint(0, len(textz)-1)])
    
    prompt = f'Пользователь задал вопрос: "{user_question}". '
    if user_data:
        prompt += f'Имя: {user_data["real_name"]}, дата рождения: {user_data["birth_date"]}. '
    prompt += 'Сделай расклад Таро на этот вопрос. Используй расклад из 3 карт: '
    prompt += '1) Суть ситуации, 2) Что помогает/мешает, 3) Возможный исход. '
    prompt += 'Выбери 3 случайные карты Таро и дай развернутый ответ на вопрос.'
    
    result = chat_with_gpt(prompt)
    
    bot.edit_message_text(f'❓Ответ на твой вопрос:\n\n{result}', message.chat.id, sent_msg.message_id, parse_mode='HTML')


def love(message):
    from baza import get_user_data
    partner_info = message.text
    user_data = get_user_data(message.from_user.id)
    
    sent_msg = bot.send_message(message.chat.id, textz[random.randint(0, len(textz)-1)])
    
    prompt = f'Нужно проверить совместимость. '
    if user_data:
        prompt += f'Первый человек: {user_data["real_name"]}, дата рождения: {user_data["birth_date"]}. '
    prompt += f'Второй человек: {partner_info}. '
    prompt += 'Используй расклад Таро на совместимость из 5 карт: '
    prompt += '1) Чувства первого, 2) Чувства второго, 3) Что связывает, 4) Препятствия, 5) Перспективы отношений. '
    prompt += 'Выбери 5 случайных карт Таро и дай подробный анализ совместимости.'
    
    result = chat_with_gpt(prompt)
    bot.edit_message_text(f'💑Анализ совместимости:\n\n{result}', message.chat.id, sent_msg.message_id, parse_mode='HTML')


def relationships(message):
    from baza import get_user_data
    situation = message.text
    user_data = get_user_data(message.from_user.id)
    
    sent_msg = bot.send_message(message.chat.id, textz[random.randint(0, len(textz)-1)])
    
    prompt = f'Сделай расклад Таро на отношения. Описание ситуации: "{situation}". '
    if user_data:
        prompt += f'Имя: {user_data["real_name"]}, дата рождения: {user_data["birth_date"]}. '
    prompt += 'Используй расклад из 4 карт: '
    prompt += '1) Текущее состояние отношений, 2) Твои истинные чувства, 3) Чувства партнера, 4) Перспективы развития. '
    prompt += 'Выбери 4 случайные карты Таро и дай детальную интерпретацию.'
    
    result = chat_with_gpt(prompt)
    bot.edit_message_text(f'💔Расклад на отношения:\n\n{result}', message.chat.id, sent_msg.message_id, parse_mode='HTML')


def generate_state_card(call):
    from baza import get_user_data
    user_data = get_user_data(call.from_user.id)
    
    prompt = 'Вытяни одну карту Таро - "Карту дня" или "Карту состояния". '
    if user_data:
        prompt += f'Для человека: {user_data["real_name"]}, дата рождения: {user_data["birth_date"]}. '
    prompt += 'Опиши значение этой карты, что она говорит о текущем состоянии человека, '
    prompt += 'его энергии, настроении и том, на что стоит обратить внимание сегодня. '
    prompt += 'Дай краткий, но емкий совет на основе этой карты.'
    
    result = chat_with_gpt(prompt)
    bot.edit_message_text(f'🧠Карта твоего состояния:\n\n{result}', call.message.chat.id, call.message.message_id, parse_mode='HTML')


def generate_matrix(callback):
    from baza import get_user_data, get_matrix, save_matrix
    user_data = get_user_data(callback.from_user.id)
    
    if not user_data or not user_data['birth_date']:
        bot.edit_message_text('❌Не могу построить матрицу без даты рождения.\n'
                            'Пожалуйста, пройди регистрацию заново.',
                            callback.message.chat.id, callback.message.message_id)
        return
    
    existing_matrix = get_matrix(callback.from_user.id)
    
    if existing_matrix:
        bot.edit_message_text(f'🪞Матрица судьбы\n\n{existing_matrix}', callback.message.chat.id, callback.message.message_id, parse_mode='HTML')
        return
    
    prompt = f'Построй матрицу судьбы (нумерологический расчет) для человека: '
    prompt += f'Имя: {user_data["real_name"]}, дата рождения: {user_data["birth_date"]}. '
    prompt += 'Рассчитай основные числа матрицы судьбы на основе даты рождения. '
    prompt += 'Включи: число жизненного пути, число судьбы, число души, таланты, задачи, кармические уроки. '
    prompt += 'Дай подробное описание каждого числа и общие рекомендации.'
    
    result = chat_with_gpt(prompt)
    save_matrix(callback.from_user.id, result)
    
    bot.edit_message_text(f'🪞Матрица судьбы\n\n{result}', callback.message.chat.id, callback.message.message_id, parse_mode='HTML')





