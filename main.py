import json
from random import randint

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
    LinkPreviewOptions
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
# response = requests.get(request, headers=headers)
# json_response = response.json()
# with open('kinopoisk.json', 'w', encoding='utf-8') as kp:
#     json.dump(json_response, kp, indent=4, ensure_ascii=False)


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
    [InlineKeyboardButton('Выбрать жанр', callback_data='genre_add'),
     InlineKeyboardButton('Выбрать длительность', callback_data='film_length_add')],
     [InlineKeyboardButton('Выбрать страну', callback_data='country_add'),
    InlineKeyboardButton('Выбрать год', callback_data='year_add')],
     [InlineKeyboardButton('Выбрать тип', callback_data='type_add'),
     InlineKeyboardButton('Выбрать рейтинг', callback_data='rate_add')],
    [InlineKeyboardButton('Вернуться', callback_data='return')]
]
markup_search = InlineKeyboardMarkup(reply_keyboard_search)

reply_keyboard_delete = [
    [InlineKeyboardButton('Удалить жанр', callback_data='genre'),
     InlineKeyboardButton('Удалить длительность', callback_data='film_length')],
    [InlineKeyboardButton('Удалить страну', callback_data='country'),
    InlineKeyboardButton('Удалить год', callback_data='year')],
    [InlineKeyboardButton('Удалить тип', callback_data='type'),
     InlineKeyboardButton('Удалить рейтинг', callback_data='rate')],
    [InlineKeyboardButton('Вернуться', callback_data='return')]
]
markup_delete = InlineKeyboardMarkup(reply_keyboard_delete)

reply_keyboard_do = [[InlineKeyboardButton('Добавить критерий', callback_data="add"), InlineKeyboardButton('Убрать критерий', callback_data="delete")],
                     [InlineKeyboardButton('Мои критерии', callback_data="my_params")],
                     [InlineKeyboardButton('Инструкция', callback_data="help")],
                     [InlineKeyboardButton('Найти', callback_data='found')]]
markup_do = InlineKeyboardMarkup(reply_keyboard_do)

reply_keyboard_return = [[InlineKeyboardButton('Вернуться', callback_data="return")]]
markup_return = InlineKeyboardMarkup(reply_keyboard_return)

reply_keyboard_swap = [[InlineKeyboardButton('Следующий фильм', callback_data='next'), InlineKeyboardButton('Вернуться', callback_data='go_back')]]
markup_swipe = InlineKeyboardMarkup(reply_keyboard_swap)


search_filters = {'genre': None, 'film_length': None, 'country': None, 'year': None, 'type': None, 'rate': None}
ru = ['Жанр', "Длительность", "Страна", "Год", "Тип", "Рейтинг"]
is_return = False
last_text = 'start'
genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = False
response_get = False
count = 0


async def button(update, context, msg='') -> None:
    global count, response_get, search_filters, is_return, last_text, length_dialogue, country_dialogue, year_dialogue, type_dialogue, rating_dialogue, genre_dialogue, json_response
    genre_dialogue = length_dialogue = country_dialogue = year_dialogue = type_dialogue = rating_dialogue = False
    is_return = False

    query = update.callback_query
    message_id = query.message.id
    await query.answer()
    print(query.data)

    if query.data == 'return':
        is_return = True
    if query.data == 'help':
        await query.edit_message_text(text="Я бот который поможет найти тебе нужный фильм!)\n"
        "\n<i>Пояснение функций:</i>\n"
        "\n<b>Выбрать жанр</b> - выдает список жанров, их существует всего 32, ты должен указать одну из цифр списка, жанры упорядочены по алфавиту.\n"
        "\n<b>Выбрать длительность</b> - предлагает ввести длину фильма или диапазон в минутах, если ввести 50-120, то бот будет искать фильмы, которые не короче 50 минут и не длиннее 120 минут.\n"
        "\n<b>Выбрать страну</b>- предлагает ввести страну по которой будет искаться фильм. Если ввести несуществующую страну, то бот скажет, что такой страны в нашем списке нет.\n"
        "\n<b>Выбрать год</b> - предлагает ввести год издания фильма или диапазон годов, если ввести 2020-2023, то бот будет искать фильмы, которые вышли не раньше 2020 года и не позже 2023 года.\n"
        "\n<b>Выбрать тип</b> - дает на выбор 5 типов, ты должен указать один из них, написав его цифру.\n"
        "\n<b>Выбрать рейтинг</b> - предлагает ввести рейтинг фильма или диапазон рейтинга, минимальный рейтинг: 0, максимальный: 10, если ввести 6-9, то бот будет искать фильмы с рейтинг не ниже 6 и не выше 9.\n"
        "\n<b>Найти</b> - ищет подходящий фильм по жанру, длине, стране, году, типу, рейтингу, автору фильма, если не указывать фильтры поиска, то бот выдаст рандомный фильм.\n"
        "\n<b>Удалить критерий</b> - предлагает удалить 1 из фильтров либо сразу все.\n"
        "\n<b>Следующий фильм</b> - выводит следующий фильм с такими же параметрами. \n<b>Лимит фильмов: 250.</b>\n"
        "\n<b>Вернуться</b> - возвращает пользователя на шаг назад.", parse_mode=ParseMode.HTML, reply_markup=markup_return)
    elif query.data == 'start' or (last_text == 'start' and is_return):
        user = update.effective_user
        await query.edit_message_text(
            f"Привет {user.mention_html()}! Я <i>Мастер по фильмам.</i> Выберите нужные вам характеристики и я найду вам нужный фильм!\n"
            f"Для начала работы со мной выберите поле с надписью <b>Приступить к поиску</b>.\n"
            f"Чтобы увидеть пояснение команд выберите поле с надписью <b>Инструкция</b>.",
            reply_markup=markup, parse_mode=ParseMode.HTML)
    elif query.data == 'start_search' or (last_text == 'start_search' and is_return):
        if not is_return:
            last_text = query.data
        await query.edit_message_text(text='Выберите что вы хотите сделать:', reply_markup=markup_do)
    elif query.data == 'add' or (last_text == 'add' and is_return):
        last_text = 'start_search'
        await query.edit_message_text(text='Выберите что вы хотите сделать:', reply_markup=markup_search)
    elif query.data == 'delete':
        await query.edit_message_text(text='Выберите что вы хотите удалить:', reply_markup=markup_delete)
    elif query.data in ['genre', 'film_length', 'country', 'year', 'type', 'rate']:
        last_text = 'start_search'
        search_filters[query.data] = None
        i = 0
        x = 0
        for key, value in search_filters.items():
            if query.data == key:
                x = i
            i += 1
        await query.edit_message_text(text=f'<b>Критерий {ru[x]} удален.</b> Выберите что вы хотите удалить:', reply_markup=markup_delete, parse_mode=ParseMode.HTML)
    elif query.data == 'genre_add' or genre_dialogue:
        last_text = 'start_search'
        text = ''
        for i in range(len(json_response_genres)):
            text += f'{i + 1}. {json_response_genres[i]['name']}\n'
        await query.edit_message_text(f'{text}\nВот список жанров фильмов, напиши одну любую цифру из доступных')
        genre_dialogue = True
    elif query.data == 'film_length_add':
        last_text = 'start_search'
        await query.edit_message_text(f'Введите длину или диапазон фильма в минутах, например: 60-120')
        length_dialogue = True
    elif query.data == 'country_add':
        last_text = 'start_search'
        await query.edit_message_text(f'Введите название страны по которой будет осуществляться поиск')
        country_dialogue = True
    elif query.data == 'year_add':
        last_text = 'start_search'
        await query.edit_message_text(f'Введите любой год в пределах разумного(1874-2024), также через "-" вы можете указать диапазон поиска: 2020-2023')
        year_dialogue = True
    elif query.data == 'type_add':
        last_text = 'start_search'
        text = ''
        for i, x in enumerate(json_response_types):
            text += f'{i + 1}. {x['name']}\n'
        await query.edit_message_text(f'{text}Вот доступные типы фильмов, укажите цифру одного из них')
        type_dialogue = True
    elif query.data == 'rate_add':
        last_text = 'start_search'
        await query.edit_message_text(f'Введите рейтинг от 0 до 10, например: 6.7, также через "-" вы можете указать диапазон поиска: 4.5-10')
        rating_dialogue = True
    elif query.data == 'found' or query.data == 'next':
        last_text = 'start_search'
        if not response_get:
            await query.edit_message_text(f'Ищу фильм, подождите...')
            params = {
                'genres.name': search_filters['genre'],
                'movieLength': search_filters['film_length'],
                'countries.name': search_filters['country'],
                'year': search_filters['year'],
                'type': search_filters['type'],
                'rating.kp': search_filters['rate'],
                'limit': 250
            }
            response = requests.get(request, headers=headers, params=params)
            json_response = response.json()
            response_get = True
        if len(json_response['docs']) != 0:
            try:
                x = randint(0, len(json_response['docs']) - 1)
                photo = json_response['docs'][x]['poster']['url'] if json_response['docs'][x]['poster']['url'] != None else open('kinopoisk.jpg', 'rb')
                name = json_response['docs'][x]['name'] if json_response['docs'][x]['name'] != None else json_response['docs'][x]['alternativeName']
                year = json_response['docs'][x]['year']
                age = json_response['docs'][x]['ageRating'] if json_response['docs'][x]['ageRating'] != None else 0

                if json_response['docs'][x]['movieLength'] != None:
                    length = f'фильма: {json_response['docs'][x]['movieLength']}'
                elif json_response['docs'][x]['seriesLength'] != None:
                    length = f'серии: {json_response['docs'][x]['seriesLength']}'
                else:
                    length = 0

                rating = json_response['docs'][x]['rating']['kp']
                if json_response['docs'][x]['description'] != None:
                    description = json_response['docs'][x]['description']
                elif json_response['docs'][x]['shortDescription'] != None:
                    description = json_response['docs'][x]['shortDescription']
                else:
                    description = f'Без описания'

                all_series = f'\nДлительность всех серий: {json_response['docs'][x]['totalSeriesLength']}' if json_response['docs'][x]['isSeries'] == True and json_response['docs'][x]['totalSeriesLength'] != None else ''
                request_web = f'https://www.kinopoisk.ru/film/{json_response['docs'][x]['id']}/'
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=f"<a href=\"{request_web}\">«{name}»</a> ({year} год, {age}+)"
                                                                                                    f"\nДлительность {length} мин.{all_series}"
                                                                                                    f"\nРейтинг фильма: {rating}\n"
                                                                                                    f"\n{description}",
                                             reply_markup=markup_swipe, parse_mode=ParseMode.HTML)
                # link_preview_options=LinkPreviewOptions(is_disabled=True)
                if count > 0:
                    await context.bot.edit_message_reply_markup(reply_markup=None, chat_id=update.effective_chat.id, message_id=int(message_id))
                del json_response['docs'][x]
                count += 1
            except Exception:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Упс.. что-то пошло не так!')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Фильмов с такими параметрами не существует, попробуйте поменять параметры.', reply_markup=markup_return)
            response_get = False
    elif query.data == 'my_params':
        text = {}
        txt = ''
        i = 0
        print(search_filters)
        for key, value in search_filters.items():
            if value == None:
                text[ru[i]] = 'Параметр не указан'
            else:
                text[ru[i]] = value
            i += 1
        for key, value in text.items():
            txt += f'<b>{key}</b>: {value}\n'
        try:
            await query.edit_message_text(f'{txt}', parse_mode=ParseMode.HTML, reply_markup=markup_do)
        except Exception:
            pass
    elif query.data == 'go_back':
        response_get = False
        await context.bot.edit_message_reply_markup(reply_markup=None, chat_id=update.effective_chat.id, message_id=int(message_id))
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите что вы хотите сделать:', reply_markup=markup_do)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я <i>Мастер по фильмам.</i> Выберите нужные вам характеристики и я найду вам нужный фильм!\n"
        f"Для начала работы со мной выберите поле с надписью <b>Приступить к поиску</b>.\n"
        f"Чтобы увидеть пояснение команд выберите поле с надписью <b>Инструкция</b>.",
        reply_markup=markup)


async def answers(update, context):
    global search_filters
    if genre_dialogue:
        if update.message.text.isdigit() and (33 > int(update.message.text) > 0):
            await update.message.reply_html(f'Вы выбрали жанр номер {update.message.text}: <b>{json_response_genres[int(update.message.text) - 1]['name']}</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
            search_filters['genre'] = json_response_genres[int(update.message.text) - 1]['name']
        else:
            await update.message.reply_text(f'Введите существующий номер!')
    elif length_dialogue:
        if update.message.text.isdigit():
            await update.message.reply_html(f'Вы ввели длительность: <b>{update.message.text} мин</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
            search_filters['film_length'] = update.message.text
        elif update.message.text.split('-')[0].isdigit() and update.message.text.split('-')[1].isdigit():
            await update.message.reply_html(f'Вы ввели диапазон длительности длительности: <b>{update.message.text} мин</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
            search_filters['film_length'] = update.message.text
        else:
            await update.message.reply_text(f'Введите число или диапазон чисел!')
    elif country_dialogue:
        for x in json_response_countries:
            if update.message.text.lower() == x['name'].lower():
                await update.message.reply_html(f'Вы выбрали страну: <b>{x['name']}</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
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
                await update.message.reply_html(f'Вы выбрали <b>{update.message.text} год</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
                search_filters['year'] = update.message.text
        elif update.message.text.split('-')[0].isdigit() and update.message.text.split('-')[1].isdigit():
            if (2025 > int(update.message.text.split('-')[0]) > 1874) and (2025 > int(update.message.text.split('-')[1]) > 1874):
                await update.message.reply_html(f'Вы выбрали диапазон <b>{update.message.text} год</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
                search_filters['year'] = update.message.text
            else:
                await update.message.reply_text(f'Числа не могут быть меньше 1874 и больше нынешнего года!')
        else:
            await update.message.reply_text(f'Введите число!')
    elif type_dialogue:
        if update.message.text.isdigit():
            if 6 > int(update.message.text) > 0:
                await update.message.reply_html(f'Вы выбрали тип номер {update.message.text}: <b>{json_response_types[int(update.message.text) - 1]['name']}</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
                search_filters['type'] = json_response_types[int(update.message.text) - 1]['name']
            else:
                await update.message.reply_text(f'Введите цифру из списка!')
        else:
            await update.message.reply_text(f'Введите цифру!')
    elif rating_dialogue:
        if isfloat(update.message.text):
            if 0.0 <= float(update.message.text) <= 10.0:
                await update.message.reply_html(f'Вы ввели рейтинг: <b>{update.message.text}</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
                search_filters['rate'] = update.message.text
            else:
                await update.message.reply_text(f'Вы можете вводить рейтинг от 2 до 10!')
        elif isfloat(update.message.text.split('-')[0]) and isfloat(update.message.text.split('-')[1]):
            if (0.0 <= float(update.message.text.split('-')[0]) <= 10.0) and (0.0 <= float(update.message.text.split('-')[1]) <= 10.0):
                await update.message.reply_html(f'Вы ввели диапозон рейтинга: <b>{update.message.text}</b>. Теперь вы можете выбрать другой фильтр или нажать на поле <b>Вернуться ⭢ Найти</b>.', reply_markup=markup_search)
                search_filters['rate'] = update.message.text
            else:
                await update.message.reply_text(f'Вы можете вводить диапазон рейтинга от 0 до 10!')
        else:
            await update.message.reply_text(f'Введите цифру!')
    else:
        await update.message.reply_html(f'Для начала диалога с ботом введите /start. <b>Слушайте что говорит бот.</b>')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answers))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()


if __name__ == '__main__':
    main()