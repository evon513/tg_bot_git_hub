import json
from random import randint

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters
import logging
from telegram.ext import Application
from config import BOT_TOKEN

headers = {"X-API-KEY": "098494fe-ff75-492d-ad4f-8833d7ff4b85"}
request = 'https://kinopoiskapiunofficial.tech/api/v2.2/films'
response = requests.get(request, headers=headers)
json_response = response.json()
# with open('kinopoisk.json', 'w') as kp:
#     json.dump(json_response, kp, ensure_ascii=False, indent=4)

request_filters = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/filters'
response_filters = requests.get(request_filters, headers=headers)
json_response_filters = response_filters.json()

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
# )
#
# logger = logging.getLogger(__name__)

reply_keyboard = [['/help', '/search'],
                  ['/start', '/close']]

reply_keyboard_search = [
    ['/author', '/country'],
    ['/rate', '/year'],
    ['/name', '/type'],
    ['/genre', '/found']
]

reply_keyboard_swap = [['/next', '/back_to_menu']]
markup_search = ReplyKeyboardMarkup(reply_keyboard_search, one_time_keyboard=False)
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup_swipe = ReplyKeyboardMarkup(reply_keyboard_swap, one_time_keyboard=False)

last_markup = markup

chose_genre = chose_author = chose_name = chose_type = chose_year = chose_rate = chose_country = False

is_choosed = False

genre = author = name = type = year = rate = country = ''


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я Мастер по фильмам. Выберите нужные вам характеристики и я найду вам нужный фильм! Для поиска фильма введите /search",
        reply_markup=markup)


async def help(update, context):
    await update.message.reply_text(
        "Я бот который поможет найти тебе нужный фильм!). Для открытия меню быстрых команд напишите /open"
        "/genre делает.."
        "/name"
        "/country"
        "/year"
        "/type"
        "/country")


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


async def genres(update, context):
    global chose_genre
    text = ''
    for i in range(len(json_response_filters['genres'])):
        text += f'{i + 1}. {json_response_filters['genres'][i]['genre']}\n'
    await update.message.reply_text(text)
    await update.message.reply_text(f"Вот список жанров фильмов, напиши одну любую цифру из доступных")
    chose_genre = True


async def answers(update, context):
    global genre, country
    if chose_genre:
        if update.message.text.isdigit() and (34 > int(update.message.text) > 0):
            await update.message.reply_text(
                f'Вы выбрали жанр номер {update.message.text}: {json_response_filters['genres'][int(update.message.text) - 1]['genre']}, теперь можете выбрать другой фильтр.')
            genre = update.message.text
        else:
            await update.message.reply_text(f'Введите существующий номер либо выберите другой фильтр')
    elif chose_author:
        pass
    elif chose_name:
        pass
    elif chose_rate:
        pass
    elif chose_country:
        for country in json_response_filters['countries']:
            if update.message.text.lower() == country['country'].lower():
                await update.message.reply_text(f'Вы выбрали страну: {update.message.text.lower()}, теперь можете выбрать другой фильтр.')
                country = update.message.text.lower().isupper()
                return
        await update.message.reply_text(f'Похоже такой страны в нашем списке нет!')
    elif chose_year:
        pass
    elif chose_type:
        pass
    else:
        await update.message.reply_text(f'Выберите фильтр либо введите команду /found для поиска фильма {genre}')


async def found(update, context):
    global response, json_response
    params = {'genres': genre,
              'type': type,
              'year': year,
              'countries': country,
              'nameRu': name,
              'ratingKinopoisk': rate}
    response = requests.get(request, headers=headers, params=params)
    json_response = response.json()
    x = randint(0, len(json_response['items']) - 1)
    request_web = f'https://www.kinopoisk.ru/film/{json_response['items'][x]['kinopoiskId']}/'
    await update.message.reply_html(f"<a href=\"{request_web}\">{json_response['items'][x]['nameRu']}</a>", reply_markup=markup_swipe)
    del json_response['items'][x]


async def next(update, context):
    global json_response
    try:
        x = randint(0, len(json_response['items']) - 1)
        request_web = f'https://www.kinopoisk.ru/film/{json_response['items'][x]['kinopoiskId']}/'
        await update.message.reply_html(f"<a href=\"{request_web}\">{json_response['items'][x]['nameRu']}</a>",
                                        reply_markup=markup_swipe)
        del json_response['items'][x]
    except Exception:
        await update.message.reply_text(f'Упс, кажись фильмов с таким фильтром больше не осталось!')


async def back(update, context):
    global genre, author, name, type, year, rate, country
    genre = author = name = type = year = rate = country = ''
    await search(update, context)


async def year(update, context):
    global chose_year
    await update.message.reply_text(f'Введите любой год в пределах разумного')
    chose_year = True


async def rate(update, context):
    global chose_rate
    await update.message.reply_text(f'Введите рейтинг от 0 до 10, например: 6.7')
    chose_rate = True


async def type(update, context):
    global chose_type
    types = ['FILM', 'TV_SERIES', 'VIDEO', 'MINI_SERIES', 'TV_SHOW']
    await update.message.reply_text(f'{types} Вот доступные типы фильмов, укажите один из них')
    chose_type = True


async def country(update, context):
    global chose_country
    await update.message.reply_text(f'Введите название страны по которой будет осуществляться поиск')
    chose_country = True


async def name(update, context):
    global chose_name
    await update.message.reply_text(f'Введите название или строку по которой мы будем искать фильм')
    chose_name = True


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler('open', open))
    application.add_handler(CommandHandler('close', close))
    application.add_handler(CommandHandler('search', search))
    application.add_handler(CommandHandler('genre', genres))
    application.add_handler(CommandHandler('found', found))
    application.add_handler(CommandHandler('next', next))

    application.add_handler(CommandHandler('name', name))
    application.add_handler(CommandHandler('year', year))
    application.add_handler(CommandHandler('type', type))
    application.add_handler(CommandHandler('country', country))
    application.add_handler(CommandHandler('rate', rate))

    application.add_handler(CommandHandler('back_to_menu', back))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answers))
    application.run_polling()


if __name__ == '__main__':
    main()
