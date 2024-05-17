import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink

from main import main, get_fresh_mining_news

load_dotenv()

TOKEN: str | None = os.getenv('TOKEN')  # Токен телеграм-бота
FILE_PATH: str | None = os.getenv('FILE_PATH')  # путь до json-файла с новостями
TG_USER_ID: str | None = os.getenv('TG_USER_ID')  # id телеграм-профиля
REFRESH_INTERVAL_SECONDS: str | None = os.getenv('REFRESH_INTERVAL_SECONDS')  # время до следующего запроса свежих новостей в секундах

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message) -> None:
    """Отправляет приветственное сообщение при старте бота."""
    start_buttons: tuple[str] = ('Свежие новости',)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    welcome_message: str = 'Здравствуйте! Для получения свежих новостей воспользуйтесь кнопкой ниже.'
    await message.reply(welcome_message, reply_markup=keyboard)


@dp.message_handler(Text(equals='Свежие новости'))
async def send_fresh_news(message: types.Message) -> None:
    """Отправляет свежие новости в telegram по кнопке 'Свежие новости'. """
    try:
        fresh_news: dict[str, dict[str, str]] = get_fresh_mining_news()
        if not fresh_news:
            await message.answer('Свежих новостей нет')
        else:
            for k, v in sorted(fresh_news.items()):
                news: str = (f"{hbold(v['article_date'])}\n"
                             f"{hlink(v['article_title'], v['article_url'])}")
                await message.answer(news)
    except exceptions.RetryAfter as e:
        await asyncio.sleep(e.timeout)
        print(f'Возникло исключение RetryAfter: {e} ')
    except Exception as ex:
        print(f'Произошла непредвиденная ошибка: {ex}')


async def check_if_fresh_news() -> None:
    """Проверяет на наличие свежих новостей и отправляет их в TG-чат."""
    while True:
        try:
            fresh_news: dict[str, dict[str, str]] | None = main()
            if fresh_news:
                for _, v in sorted(fresh_news.items()):
                    news: str = (f"{hbold(v['article_date'])}\n"
                                 f"{hbold(v['article_category'])}\n"
                                 f"{hlink(v['article_title'], v['article_url'])}\n")
                    await bot.send_message(TG_USER_ID, news)
        except exceptions.RetryAfter as e:
            await asyncio.sleep(e.timeout)
            print(f'Возникло исключение RetryAfter: {e} ')
        except Exception as ex:
            print(f'Произошла непредвиденная ошибка: {ex}')
        await asyncio.sleep(int(REFRESH_INTERVAL_SECONDS))


if __name__ == '__main__':
    try:
        asyncio.run(check_if_fresh_news())
    except KeyboardInterrupt:
        print('Бот остановлен пользователем.')
    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')
    finally:
        executor.start_polling(dp)
