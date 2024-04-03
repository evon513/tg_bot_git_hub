import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
import logging
from telegram.ext import Application
from config import BOT_TOKEN

headers = {"X-API-KEY": "098494fe-ff75-492d-ad4f-8833d7ff4b85"}
request = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/filters'
response = requests.get(request, headers=headers)
json_response = response.json()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/help', '/search'],
                  ['/start']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я Мастер по фильмам. Выберите нужные вам характеристики и я найду вам нужный фильм! Для поиска фильма введите /search",
        reply_markup=markup)


async def help(update, context):
    await update.message.reply_text(
        "Я бот который поможет найти тебе нужный фильм!). Для открытия меню быстрых команд напишите /open")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()


if __name__ == '__main__':
    main()
