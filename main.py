import random 
import spreads
import admin
from config import bot 
from markup import menu_markup
from baza import update_info, user_exists
from registration import get_name
from premium import show_premium_menu


menu_text = ['Привет! 👋 Я здесь, чтобы помочь тебе узнать больше о себе и твоей жизни через Таро и нумерологию.',
            'Привет! 🌟 Готов показать, что карты и числа говорят о твоем дне, неделе, месяце и году.',
            'Привет! 🔮 Хочешь получить совет на сегодня или проверить совместимость с кем-то? Я помогу.',
            'Привет! 💫 Здесь ты можешь узнать свои сильные стороны, слабости и получить рекомендации от карт и матрицы судьбы.',
            'Привет! 🃏 Я помогу сделать расклад на любой период, проверить совместимость или составить матрицу судьбы — выбери, что тебе интересно.']


@bot.message_handler(commands=['start', 'menu'])
def start_bot(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''
    full_name = first_name + (' ' + last_name if last_name else '')
    update_info(user_id, message.from_user.username, full_name)
    rand = random.randint(0, len(menu_text) - 1)
    if not user_exists(user_id):
        get_name(message)
    else: 
        bot.send_message(message.chat.id, menu_text[rand], reply_markup=menu_markup()) 


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '🤖Версия 1.0 бета \n👨🏼‍💻DurnovP') 

@bot.message_handler(commands=['reg'])
def re_registration(message):
    bot.send_message(message.chat.id, '🔄Начинаем регистрацию заново...')
    get_name(message)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''
    full_name = first_name + (' ' + last_name if last_name else '')
    update_info(message.from_user.id, message.from_user.username, full_name)
    if message.text == '🎴Меню':
        from markup import spread_markup
        bot.send_message(message.chat.id, '🌞Расклад можно заказать на день, неделю, месяц или год.\n\n'
                                        '💑 / 💔 Для анализа нужно имя и дата рождения человека', reply_markup=spread_markup())
    elif message.text == '🌟Подписка':
        show_premium_menu(message)
    else:
        bot.send_message(message.chat.id, '🤷Я не понимаю эту команду. Пожалуйста, выбери опцию из меню.', reply_markup=menu_markup())


if __name__ == '__main__':
    from baza import create_baza
    create_baza()
    print('🤖 Бот запущен!')
    bot.infinity_polling()
