import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
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
                  ['/start', '/close']]

reply_keyboard_search = [
                         ['/author', '/country'],
                         ['/rate', '/year'],
                         ['/name', '/type'],
                         ['/genre', '/found']
                        ]
markup_search = ReplyKeyboardMarkup(reply_keyboard_search, one_time_keyboard=False)
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

last_markup = markup


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я Мастер по фильмам. Выберите нужные вам характеристики и я найду вам нужный фильм! Для поиска фильма введите /search",
        reply_markup=markup)


async def help(update, context):
    await update.message.reply_text(
        "Я бот который поможет найти тебе нужный фильм!). Для открытия меню быстрых команд напишите /open")


async def close(update, context):
    await update.message.reply_text('Ок, для открытия клавиатуры введите /open', reply_markup=ReplyKeyboardRemove())


async def open(update, context):
    await update.message.reply_text('Ок, для закрытия клавиатуры введите /close', reply_markup=last_markup)


async def search(update, context):
    global last_markup
    text = ''
    for j in range(len(reply_keyboard_search)):
        for i in range(len(reply_keyboard_search[j])):
            text += f'{reply_keyboard_search[j][i]}\n'
    await update.message.reply_text(text)
    await update.message.reply_text(f"Вот список доступных фильтров", reply_markup=markup_search)
    last_markup = markup_search

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler('open', open))
    application.add_handler(CommandHandler('close', close))
    application.add_handler(CommandHandler('search', search))
    application.run_polling()


if __name__ == '__main__':
    main()
