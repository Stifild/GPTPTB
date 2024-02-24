from random import randint

import telebot
from telebot.types import ReplyKeyboardMarkup

from iop import IOP, GPT

clean_markup = telebot.types.ReplyKeyboardRemove()
murckup1 = ReplyKeyboardMarkup(resize_keyboard=True)
murckup1.add('Продолжи', 'Конец')
murckup2 = ReplyKeyboardMarkup(resize_keyboard=True)
murckup2.add('Конец')
io = IOP()
gpt = GPT(system_content="You're a programming assistant")

bot = telebot.TeleBot(token=io.bot_api)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Можешь ввести любую задачу, и я постараюсь её решить\nЕсли напишешь "продолжи", я продолжу объяснять задачу\nДля завершения диалога напиши "конец"', reply_markup=clean_markup)

@bot.message_handler(commands=['log'])
def send_log(message):
    with open('logs.log', 'rb') as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(content_types=['text'])
def message_processing(message: telebot.types.Message):
    if message.text.lower() == 'конец':
        gpt.clear_history()
        bot.send_message(message.chat.id, "До новых встреч!", reply_markup=clean_markup)
        return
    request_tokens = gpt.count_tokens(message.text)
    if request_tokens > gpt.MAX_TOKENS:
        bot.send_message(message.chat.id, "Запрос несоответствует кол-ву токенов\nИсправьте запрос", reply_markup=murckup2)
        return
    if message.text.lower() != 'продолжи':
        gpt.clear_history()
    json = gpt.make_promt(message.text)
    resp = gpt.send_request(json)
    response = gpt.process_resp(resp)
    if not response[0]:
        bot.send_message(message.chat.id, "Не удалось выполнить запрос...")
    bot.send_message(message.chat.id, response[1], reply_markup=murckup1, parse_mode='HTML')



bot.infinity_polling()