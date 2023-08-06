import logging
import os
import openai
import telegram
from telegram import Update
from telegram.ext import (
    Updater, Filters, MessageHandler, CommandHandler, CallbackContext)
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from gtts import gTTS
from data import HOBBY, HELP, WAKE_UP_START, WAKE_UP_END, COMMANDS

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GPT_TOKEN = os.getenv('GPT_TOKEN')
openai.api_key = GPT_TOKEN

FORMAT_LOG = '%(asctime)s %(levelname)s %(filename)s[%(lineno)d] %(message)s'
logging.basicConfig(format=FORMAT_LOG, level=logging.INFO)

updater = Updater(token=TELEGRAM_TOKEN)
button = ReplyKeyboardMarkup(
    [
        ['Селфи', 'Школа', 'Хобби'],
        ['GPT', 'SQL|NoSQL', '1ove'],
        ['Исходники бота']
    ],
    resize_keyboard=True,
)

RETRY_TIME = 10


def convert_text_to_voice(text):
    """Конвертируем текст и голосовое сообщение."""
    tts = gTTS(text=text, lang="ru", slow=False)
    name = "content/say.mp3"
    tts.save(name)
    return name


def text_from_gpt(text):
    """Запрос к GPT. Возвращает текстовый ответ."""
    response = openai.Completion.create(
        prompt=text,
        engine='text-davinci-003',
        max_tokens=2000,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=15
    )
    if response and response.choices:
        logging.info('Сервер gpt отвечает')
        return response.choices[0].text.strip()
    else:
        return None


def voice_to_text_from_gpt(file):
    """Преобразуем голосовое сообщение в текст через GPT."""
    result = openai.Audio.transcribe(
        api_key=GPT_TOKEN,
        model='whisper-1',
        file=file,
        response_format='text'
    )
    logging.info('голосовое сообщение преобразованно в текст')
    return result


def send_message(bot, message):
    """Отправка сообщения."""
    logging.info(f'Сообщение отправлено: {message}')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def introduce(update, context):
    """Бот рассказывает о своем функционале."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=HELP,
        reply_markup=button,
    )


def wake_up(update, context):
    """Включение бота."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=WAKE_UP_START,
        reply_markup=button,
    )
    context.bot.send_photo(
        chat_id=chat.id,
        photo=open('content/task.jpg', 'rb')
    )
    context.bot.send_message(
        chat_id=chat.id,
        text=WAKE_UP_END,
        reply_markup=button,
    )


def get_voice(update: Update, context: CallbackContext) -> None:
    """Получаем голосовое сообщение от пользователя."""
    new_file = context.bot.get_file(update.message.voice.file_id)
    new_file.download("voice_note.ogg")
    file = open('voice_note.ogg', 'rb')
    result = voice_to_text_from_gpt(file)
    file.close()
    os.remove('voice_note.ogg')

    ANSWER = False
    for key in COMMANDS.keys():
        for word in COMMANDS[key]:
            if result.__contains__(word):
                if key == 'hello':
                    say_hi(update, context),
                elif key == 'selfie':
                    send_last_selfie(update, context)
                elif key == 'shcool':
                    send_shcool_pic(update, context)
                elif key == 'hobby':
                    my_hobby(update, context)
                elif key == 'gpt':
                    send_voice_about_gpt(update, context)
                elif key == 'sql':
                    send_voice_about_sql(update, context)
                elif key == 'love':
                    send_voice_about_love(update, context)
                ANSWER = True
                break
        if ANSWER is True:
            break
    if not ANSWER:
        chat = update.effective_chat
        context.bot.send_message(
            chat_id=chat.id,
            text=f'Запрос "{result}" не выполнен.',
        )


def say_hi(update, context):
    """Отправка сообщения."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, я Bot!',
    )


def send_shcool_pic(update, context):
    """Отправка фото из школы."""
    chat = update.effective_chat
    context.bot.send_photo(
        chat_id=chat.id,
        photo=open('content/old.jpg', 'rb')
    )


def send_last_selfie(update, context):
    """Отправка последнего селфи."""
    chat = update.effective_chat
    context.bot.send_photo(
        chat_id=chat.id,
        photo=open('content/last_selfie.jpg', 'rb')
    )


def my_hobby(update, context):
    """Отправка текса про увлечение."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=HOBBY,
    )


def send_voice_about_gpt(update, context):
    """Отправка голосового сообщения про gpt."""
    chat = update.effective_chat
    context.bot.send_voice(
        chat_id=chat.id,
        voice=open('content/about_gpt.mp3', 'rb')
    )


def creat_voice_about_gpt(update, context):
    """Служебная функция, не используется."""
    text = (
        "напиши рассказ что такое GPT не более 2000 символов,"
        "так, чтобы понял ребенок и постарайся писать как человек."
        "Закончи рассказ словами - Например, этот рассказ написан с "
        "помощью GPT.")
    chat = update.effective_chat
    context.bot.send_voice(
        chat_id=chat.id,
        voice=open(
            convert_text_to_voice(text_from_gpt(text)),
            'rb'
        )
    )


def send_voice_about_sql(update, context):
    """Отправка голосового сообщения про sql."""
    chat = update.effective_chat
    context.bot.send_voice(
        chat_id=chat.id,
        voice=open(
            'content/sql_vs_nosql.mp3',
            'rb'
        )
    )


def send_voice_about_love(update, context):
    """Отправка голосового сообщения про любовь."""
    chat = update.effective_chat
    context.bot.send_voice(
        chat_id=chat.id,
        voice=open(
            'content/love.ogg',
            'rb'
        )
    )


def send_git_hub_rep(update, context):
    """Отправка текса про увлечение."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text="https://github.com/Life31/1ife3_1_bot",
    )


def tolk_to_me_gpt(update, context):
    """Отправка сообщения в GPT и вывод ответа."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=text_from_gpt(update.message.text),
    )


def main():
    """Главный цикл бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    if (GPT_TOKEN or TELEGRAM_TOKEN) is None:
        logging.error('Отсутствуют обязательные переменные окружения.')
    message = 'Бот начал работать'
    send_message(bot, message)

    while True:
        updater.dispatcher.add_handler(CommandHandler('start', wake_up))
        updater.dispatcher.add_handler(CommandHandler('help', introduce))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.voice, get_voice))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Школа'), send_shcool_pic))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Селфи'), send_last_selfie))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Хобби'), my_hobby))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('GPT'), send_voice_about_gpt))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('SQL|NoSQL'), send_voice_about_sql))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('1ove'), send_voice_about_love))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Исходники бота'), send_git_hub_rep))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Привет'), say_hi))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text, tolk_to_me_gpt))

        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
