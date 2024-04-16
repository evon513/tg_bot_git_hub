import json
from random import randint

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
import logging
from telegram.ext import Application
from config import BOT_TOKEN


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


headers = {"X-API-KEY": "13KFM42-2QQ40P8-HP85Q09-8EV5DWQ"}
request = f'https://api.kinopoisk.dev/v1.4/movie'
json_response = ''

with open('kinopoisk_genres.json', encoding='utf-8') as kp:
    json_response_genres = json.load(kp)

with open('kinopoisk_types.json', encoding='utf-8') as kp:
    json_response_types = json.load(kp)

with open('kinopoisk_countries.json', encoding='utf-8') as kp:
    json_response_countries = json.load(kp)

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
# )
#
# logger = logging.getLogger(__name__)

reply_keyboard = [[InlineKeyboardButton('Инструкция', callback_data="help"), InlineKeyboardButton('Приступить к поиску', callback_data="start_search")]]
markup = InlineKeyboardMarkup(reply_keyboard)

reply_keyboard_search = [
    [InlineKeyboardButton('Выбрать жанр', callback_data='genre'),
     InlineKeyboardButton('Выбрать длительность', callback_data='film_length')],
     [InlineKeyboardButton('Выбрать страну', callback_data='country'),
    InlineKeyboardButton('Выбрать год', callback_data='year')],
     [InlineKeyboardButton('Выбрать тип', callback_data='type'),
     InlineKeyboardButton('Выбрать рейтинг', callback_data='rate')],
    [InlineKeyboardButton('Инструкция', callback_data='help'), InlineKeyboardButton('Вернуться', callback_data='return')],
[   InlineKeyboardButton('Найти', callback_data='found')]
]
markup_search = InlineKeyboardMarkup(reply_keyboard_search)

reply_keyboard_delete = [
    [InlineKeyboardButton('Удалить жанр', callback_data='1'),
     InlineKeyboardButton('Удалить длительность', callback_data='2')],
    [InlineKeyboardButton('Удалить страну', callback_data='3'),
    InlineKeyboardButton('Удалить год', callback_data='4')],
    [InlineKeyboardButton('Удалить тип', callback_data='5'),
     InlineKeyboardButton('Удалить рейтинг', callback_data='6')],
    [InlineKeyboardButton('Вернуться', callback_data='return')],
    [InlineKeyboardButton('Инструкция', callback_data='help')]
]
markup_delete = InlineKeyboardMarkup(reply_keyboard_delete)

reply_keyboard_do = [[InlineKeyboardButton('Добавить критерий', callback_data="add"), InlineKeyboardButton('Убрать критерий', callback_data="delete")],
                  [InlineKeyboardButton('Инструкция', callback_data="help")]]
markup_do = InlineKeyboardMarkup(reply_keyboard_do)

reply_keyboard_return = [[InlineKeyboardButton('Вернуться', callback_data="return")]]
markup_return = InlineKeyboardMarkup(reply_keyboard_return)

reply_keyboard_swap = [['/next', '/back_to_menu']]
markup_swipe = ReplyKeyboardMarkup(reply_keyboard_swap, one_time_keyboard=False)

last_markup = markup

search_filters = {'genre': None, 'film_length': None, 'country': None, 'year': None, 'type': None, 'rate': None}
is_return = False
last_text = 'start'
genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = delete_param_dialogue = False

message_id = 0

async def button(update, context) -> None:
    global search_filters, is_return, last_text, length_dialogue
    query = update.callback_query
    await query.answer()
    message_id = query.message.message_id
    query.delete_message()
    print(message_id)
    is_return = False
    if query.data == 'return':
        is_return = True
    if query.data == 'help':
        await query.edit_message_text(text="Я бот который поможет найти тебе нужный фильм!). Для открытия меню быстрых команд напишите /open\n"
        "\nПояснение функций:\n"
        "\n<b>Выбрать жанр</b> - выдает список жанров, их существует всего 32, ты должен указать одну из цифр списка, жанры упорядочены по алфавиту.\n"
        "\n<b>Выбрать длительность</b> Предлагает ввести длину фильма или диапазон в минутах, если ввести 50-120, то бот будет искать фильмы, которые не короче 50 минут и не длиннее 120 минут.\n"
        "\n<b>Выбрать страну</b> Предлагает ввести страну по которой будет искаться фильм. Если ввести несуществующую страну, то бот скажет, что такой страны в нашем списке нет.\n"
        "\n<b>Выбрать год</b> Предлагает ввести год издания фильма или диапазон годов, если ввести 2020-2023, то бот будет искать фильмы, которые вышли не раньше 2020 года и не позже 2023 года.\n"
        "\n<b>Выбрать тип</b> Дает на выбор 5 типов, ты должен указать один из них, написав его цифру.\n"
        "\n<b>Выбрать рейтинг</b> Предлагает ввести рейтинг фильма или диапазон рейтинга, минимальный рейтинг: 0, максимальный: 10, если ввести 6-9, то бот будет искать фильмы с рейтинг не ниже 6 и не выше 9.\n"
        "\n<b>Найти</b> Ищет подходящий фильм по жанру, длине, стране, году, типу, рейтингу, автору фильма, если не указывать фильтры поиска, то бот выдаст рандомный фильм. ВАЖНО: если снова нажать на команду, будет создаваться новый запрос и фильмы будут повторяться.\n"
        "\n<b>Удалить критерий</b> Предлагает удалить 1 из фильтров либо сразу все\n"
        "\n/next Ищет фильмы с указанными параметрами. \nЛимит фильмов: 10.\n"
        "\n/back_to_menu Сбрасывает фильтры и возвращает пользователя обратно ко всем возможным командам.", parse_mode=ParseMode.HTML, reply_markup=markup_return)
    elif query.data == 'start_search' or (last_text == 'start_search' and is_return):
        if not is_return:
            last_text = query.data
        await query.edit_message_text(text='Выберите что вы хотите сделать:', reply_markup=markup_do)
    elif query.data == 'add' or (last_text == 'add' and is_return):
        if not is_return and last_text != 'start_search':
            last_text = query.data
        else:
            last_text = 'start_search'
        await query.edit_message_text(text='Выберите что вы хотите сделать:', reply_markup=markup_search)
    elif query.data == 'delete':
        await query.edit_message_text(text='Выберите что вы хотите удалить:', reply_markup=markup_delete)
    elif query.data in ['1', '2', '3', '4', '5', '6']:
        search_filters[int(query.data) - 1] = None
        await query.edit_message_text(text='<b>Критерий удален.</b> Выберите что вы хотите удалить:', reply_markup=markup_delete)
    elif query.data == 'start' or (last_text == 'start' and is_return):
        user = update.effective_user
        await query.edit_message_text(
            f"Привет {user.mention_html()}! Я <i>Мастер по фильмам.</i> Выберите нужные вам характеристики и я найду вам нужный фильм!\n"
            f"Для начала работы со мной выберите поле с надписью <b>Приступить к поиску</b>.\n"
            f"Чтобы увидеть пояснение команд выберите поле с надписью <b>Инструкция</b>",
            reply_markup=markup, parse_mode=ParseMode.HTML)
    elif query.data == 'film_length':
        last_text = 'add'
        await query.edit_message_text(f'Введите длину или диапазон фильма в минутах, например: 60-120', reply_markup=markup_return)
        length_dialogue = True
    print(query)

async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я <i>Мастер по фильмам.</i> Выберите нужные вам характеристики и я найду вам нужный фильм!\n"
        f"Для начала работы со мной выберите поле с надписью <b>Приступить к поиску</b>.\n"
        f"Чтобы увидеть пояснение команд выберите поле с надписью <b>Инструкция</b>",
        reply_markup=markup)


async def genre_function(update, context):
    global genre_dialogue, length_dialogue, country_dialogue, year_dialogue, type_dialogue, rating_dialogue, delete_param_dialogue
    genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = delete_param_dialogue = False
    text = ''
    for i in range(len(json_response_genres)):
        text += f'{i + 1}. {json_response_genres[i]['name']}\n'
    await update.message.reply_text(text)
    await update.message.reply_text(f"Вот список жанров фильмов, напиши одну любую цифру из доступных")
    genre_dialogue = True


async def country_function(update, context):
    global genre_dialogue, length_dialogue, country_dialogue, year_dialogue, type_dialogue, rating_dialogue, delete_param_dialogue
    genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = delete_param_dialogue = False
    await update.message.reply_text(f'Введите название страны по которой будет осуществляться поиск')
    country_dialogue = True


async def year_function(update, context):
    global genre_dialogue, length_dialogue, country_dialogue, year_dialogue, type_dialogue, rating_dialogue, delete_param_dialogue
    genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = delete_param_dialogue = False
    await update.message.reply_text(f'Введите любой год в пределах разумного(1874-2024), также через "-" вы можете указать диапазон поиска: 2020-2023')
    year_dialogue = True


async def type_function(update, context):
    global genre_dialogue, length_dialogue, country_dialogue, year_dialogue, type_dialogue, rating_dialogue, delete_param_dialogue
    genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = delete_param_dialogue = False
    text = ''
    for i, x in enumerate(json_response_types):
        text += f'{i + 1}. {x['name']}\n'
    await update.message.reply_text(f'{text}Вот доступные типы фильмов, укажите цифру одного из них')
    type_dialogue = True


async def rate_function(update, context):
    global genre_dialogue, length_dialogue, country_dialogue, year_dialogue, type_dialogue, rating_dialogue, delete_param_dialogue
    genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = delete_param_dialogue = False
    await update.message.reply_text(f'Введите рейтинг от 0 до 10, например: 6.7, также через "-" вы можете указать диапазон поиска: 4.5-10')
    rating_dialogue = True


async def found(update, context):
    global json_response, last_markup
    params = {
              'genres.name': search_filters['genre'],
              'movieLength': search_filters['film_length'],
              'countries.name': search_filters['country'],
              'year': search_filters['year'],
              'type': search_filters['type'],
              'rating.kp': search_filters['rate'],
              'limit': 250
              }
    await update.message.reply_text(f'Ищу фильм, подождите...')
    response = requests.get(request, headers=headers, params=params)
    print(response)
    json_response = response.json()

    try:
        x = randint(0, len(json_response['docs']) - 1)

        name = json_response['docs'][x]['name'] if json_response['docs'][x]['name'] != None else json_response['docs'][x]['alternativeName']
        year = json_response['docs'][x]['year']
        age = json_response['docs'][x]['ageRating'] if json_response['docs'][x]['ageRating'] != None else 0
        length = f'фильма: {json_response['docs'][x]['movieLength']}' if json_response['docs'][x]['movieLength'] != None else f'серии: {json_response['docs'][x]['seriesLength']}'
        rating = json_response['docs'][x]['rating']['kp']
        description = json_response['docs'][x]['description'] if json_response['docs'][x]['description'] != '' else json_response['docs'][x]['shortDescription']
        all_series = f'\nДлительность всех серий: {json_response['docs'][x]['totalSeriesLength']}' if json_response['docs'][x]['isSeries'] == True and json_response['docs'][x]['totalSeriesLength'] != None else ''

        request_web = f'https://www.kinopoisk.ru/film/{json_response['docs'][x]['id']}/'

        await update.message.reply_html(f"<a href=\"{request_web}\">«{name}»</a> ({year} год, {age}+)"
                                        f"\nДлительность {length} мин.{all_series}"
                                        f"\nРейтинг фильма: {rating}\n"
                                        f"\n{description}",
                                        reply_markup=markup_swipe)
        del json_response['docs'][x]
        last_markup = markup_swipe
    except Exception:
        await update.message.reply_text('Упс.. что-то пошло не так!')


async def next(update, context):
    global json_response
    try:
        x = randint(0, len(json_response['docs']) - 1)

        name = json_response['docs'][x]['name'] if json_response['docs'][x]['name'] != None else \
        json_response['docs'][x]['alternativeName']
        year = json_response['docs'][x]['year']
        age = json_response['docs'][x]['ageRating'] if json_response['docs'][x]['ageRating'] != None else 0
        length = f'фильма: {json_response['docs'][x]['movieLength']}' if json_response['docs'][x][
                                                                             'movieLength'] != None else f'серии: {json_response['docs'][x]['seriesLength']}'
        rating = json_response['docs'][x]['rating']['kp']
        description = json_response['docs'][x]['description'] if json_response['docs'][x]['description'] != '' else \
        json_response['docs'][x]['shortDescription']
        all_series = f'\nДлительность всех серий: {json_response['docs'][x]['totalSeriesLength']}' if \
        json_response['docs'][x]['isSeries'] == True and json_response['docs'][x]['totalSeriesLength'] != None else ''

        request_web = f'https://www.kinopoisk.ru/film/{json_response['docs'][x]['id']}/'

        await update.message.reply_html(f"<a href=\"{request_web}\">«{name}»</a> ({year} год, {age}+)"
                                        f"\nДлительность {length} мин.{all_series}"
                                        f"\nРейтинг фильма: {rating}\n"
                                        f"\n{description}",
                                        reply_markup=markup_swipe)
        del json_response['docs'][x]
    except Exception:
        await update.message.reply_text(f'Упс, кажись фильмов с таким фильтром больше не осталось!')


async def back(update, context):
    global search_filters
    search_filters = {'genre': None, 'film_length': None, 'country': None, 'year': None, 'type': None, 'rate': None}
    await search(update, context)


async def answers(update, context):
    global search_filters
    if genre_dialogue:
        if update.message.text.isdigit() and (33 > int(update.message.text) > 0):
            await update.message.reply_text(
                f'Вы выбрали жанр номер {update.message.text}: {json_response_genres[int(update.message.text) - 1]['name']}, теперь можете выбрать другой фильтр или ввести команду /found')
            search_filters['genre'] = json_response_genres[int(update.message.text) - 1]['name']
        else:
            await update.message.reply_text(f'Введите существующий номер!')
    elif length_dialogue:
        if update.message.text.isdigit():
            await update.message.reply_text(f'Вы ввели длительность: {update.message.text} мин. Теперь вы можете выбрать другой фильтр или ввести команду /found')
            search_filters['film_length'] = update.message.text
        elif update.message.text.split('-')[0].isdigit() and update.message.text.split('-')[1].isdigit():
            await update.message.reply_text(f'Вы ввели диапазон длительности длительности: {update.message.text} мин. Теперь вы можете выбрать другой фильтр или ввести команду /found')
            search_filters['film_length'] = update.message.text
        else:
            await update.message.reply_text(f'Введите число или диапазон чисел!')
    elif country_dialogue:
        for x in json_response_countries:
            if update.message.text.lower() == x['name'].lower():
                await update.message.reply_text(f'Вы выбрали страну: {x['name']}. Теперь вы можете выбрать другой фильтр или ввести команду /found')
                search_filters['country'] = x['name']
                return
        await update.message.reply_text(f'Похоже такой страны в нашем списке нет!')
    elif year_dialogue:
        if update.message.text.isdigit():
            if int(update.message.text) > 2024:
                await update.message.reply_text(f'Фильмов из будущего у нас нет, приходите в {update.message.text} году!')
            elif int(update.message.text) < 1874:
                await update.message.reply_text(f'Фильмы начинаются с 1874 года!')
            else:
                await update.message.reply_text(f'Вы выбрали {update.message.text} год. Теперь вы можете выбрать другой фильтр или ввести команду /found')
                search_filters['year'] = update.message.text
        elif update.message.text.split('-')[0].isdigit() and update.message.text.split('-')[1].isdigit():
            if (2025 > int(update.message.text.split('-')[0]) > 1874) and (2025 > int(update.message.text.split('-')[1]) > 1874):
                await update.message.reply_text(f'Вы выбрали диапазон {update.message.text} год. Теперь вы можете выбрать другой фильтр или ввести команду /found')
                search_filters['year'] = update.message.text
            else:
                await update.message.reply_text(f'Числа не могут быть меньше 1874 и больше нынешнего года!')
        else:
            await update.message.reply_text(f'Введите число!')
    elif type_dialogue:
        if update.message.text.isdigit():
            if 6 > int(update.message.text) > 0:
                await update.message.reply_text(f'Вы выбрали тип номер {update.message.text}: {json_response_types[int(update.message.text) - 1]['name']}. Теперь вы можете выбрать другой фильтр или ввести команду /found')
                search_filters['type'] = json_response_types[int(update.message.text) - 1]['name']
            else:
                await update.message.reply_text(f'Введите цифру из списка!')
        else:
            await update.message.reply_text(f'Введите цифру!')
    elif rating_dialogue:
        if isfloat(update.message.text):
            if 0.0 <= float(update.message.text) <= 10.0:
                await update.message.reply_text(f'Вы ввели рейтинг: {update.message.text}. Теперь вы можете выбрать другой фильтр или ввести команду /found')
                search_filters['rate'] = update.message.text
            else:
                await update.message.reply_text(f'Вы можете вводить рейтинг от 2 до 10!')
        elif isfloat(update.message.text.split('-')[0]) and isfloat(update.message.text.split('-')[1]):
            if (0.0 <= float(update.message.text.split('-')[0]) <= 10.0) and (0.0 <= float(update.message.text.split('-')[1]) <= 10.0):
                await update.message.reply_text(f'Вы ввели диапозон рейтинга: {update.message.text}. Теперь вы можете выбрать другой фильтр или ввести команду /found')
                search_filters['rate'] = update.message.text
            else:
                await update.message.reply_text(f'Вы можете вводить диапазон рейтинга от 0 до 10!')
        else:
            await update.message.reply_text(f'Введите цифру!')
    elif delete_param_dialogue:
        if update.message.text.isdigit():
            if 0 < int(update.message.text) < 8:
                if int(update.message.text) == 1:
                    await update.message.reply_text(f'Вы удалили все параметры. Можете задать новые или написать /found для поиска фильма')
                    search_filters = {'genre': None, 'film_length': None, 'country': None, 'year': None, 'type': None, 'rate': None}
                else:
                    for i, key in enumerate(search_filters):
                        if i == int(update.message.text) - 2:
                            search_filters[key] = None
                            await update.message.reply_text(f'Вы удалили параметр: {key}')
            else:
                await update.message.reply_text(f'Введите цифру из списка!')
        else:
            await update.message.reply_text(f'Введите цифру!')
    else:
        await update.message.reply_text(f'Выберите фильтр либо введите команду /found для поиска фильма!')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))

    application.add_handler(CommandHandler('genre', genre_function))
    application.add_handler(CommandHandler('country', country_function))
    application.add_handler(CommandHandler('year', year_function))
    application.add_handler(CommandHandler('type', type_function))
    application.add_handler(CommandHandler('rate', rate_function))

    application.add_handler(CommandHandler('found', found))

    application.add_handler(CommandHandler('next', next))
    application.add_handler(CommandHandler('back_to_menu', back))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answers))

    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()


if __name__ == '__main__':
    main()