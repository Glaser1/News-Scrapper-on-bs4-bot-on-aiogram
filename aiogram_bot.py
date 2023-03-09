import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink

from scrapper import main

load_dotenv()

bot = Bot(token=os.getenv('token'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
FILE_PATH = os.getenv('file_path')
USER_ID = os.getenv('tg_user_id')


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    start_buttons = ('Свежие новости',)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    welcome_message = 'Здравствуйте! Для получения свежих новостей воспользуйтесь кнопкой ниже.'
    await message.reply(welcome_message, reply_markup=keyboard)


@dp.message_handler(Text(equals='Свежие новости'))
async def send_fresh_news(message: types.Message):
    """ Отправить свежие новости в telegram по кнопке 'Свежие новости'. """
    fresh_news = main()
    if not fresh_news:
        await message.answer('Свежих новостей нет')
    else:
        for k, v in sorted(fresh_news.items()):
            news = (f"{hbold(v['article_date'])}\n"
                    f"{hlink(v['article_title'], v['article_url'])}")
            try:
                await message.answer(news)
            except exceptions.RetryAfter as e:
                await asyncio.sleep(e.timeout)


async def check_if_fresh_news():
    """ Проверка на наличие свежих новостей каждые 2 часа и их автоматическая отправка в tg-чат. """
    while True:
        fresh_news = main()
        if fresh_news:
            for k, v in sorted(fresh_news.items()):
                news = (f"{hbold(v['article_date'])}\n"
                        f"{hlink(v['article_title'], v['article_url'])}")
                try:
                    await bot.send_message(USER_ID, news)
                except exceptions.RetryAfter as e:
                    await asyncio.sleep(e.timeout)
        else:
            await bot.send_message(USER_ID, 'Новостей нет')
        await asyncio.sleep(10)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_if_fresh_news())
    executor.start_polling(dp)
