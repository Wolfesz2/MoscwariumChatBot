import array
import aiogram
from aiogram.dispatcher.filters import state
from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, message
from aiogram.utils import executor

from Config import TOKEN, HOST, PASSWORD, DB_NAME, USER, PORT
from Utils import States
import psycopg2


# функция для очистки строки
def clear_str(string):
    trans_table = {ord("'"): None, ord('('): None, ord(')'): None, ord(','): None}
    return string.translate(trans_table)


# подключение к Базе данных
connect = psycopg2.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD,
    database=DB_NAME,
    options="-c search_path=Main")


# Все выборки из базы данных
with connect:
    with connect.cursor() as cursor:
        # Категории
        cursor.execute('SELECT "id_Categories" FROM "Main"."Categories" ORDER BY "id_Categories" ASC ')
        select = cursor.fetchall()
        CatIdTuple = []
        for i in select:
            CatIdTuple.append(int(clear_str(str(i))))
        CategoriesTable = []
        for i in CatIdTuple:  # Построчная выборка всей таблицы
            cursor.execute(f""" select * from "Main"."Categories" where "id_Categories"={i} """)
            CategorySelect = cursor.fetchone()
            DBCategoryId = CategorySelect[0]
            DBCategoryName = CategorySelect[1]
            # Добавление строк из таблицы Questions в массив CategoriesTable[строка][столбец]
            CategoriesTable.append(list(map(str, f'{DBCategoryId}|{DBCategoryName}'.split('|'))))
        # Вопросы
        cursor.execute('SELECT "id_Questions" FROM "Main"."Questions" ORDER BY "id_Questions" ASC ')
        select = cursor.fetchall()
        QuesIdTuple = []
        for i in select:
            QuesIdTuple.append(int(clear_str(str(i))))
        QuestionsTable = []
        for i in QuesIdTuple:  # Построчная выборка всей таблицы
            cursor.execute(f""" select * from "Main"."Questions" where "id_Questions"={i} """)
            QueSelect = cursor.fetchone()
            DBQuestionId = QueSelect[0]
            DBCategoryId = QueSelect[1]
            DBQuestion = QueSelect[2]
            DBAnswer = QueSelect[3]
            # Добавление строк из таблицы Questions в массив Questions[строка][столбец]
            QuestionsTable.append(list(map(str, f'{DBQuestionId}|{DBCategoryId}|{DBQuestion}|{DBAnswer}'.split('|'))))
        # Подвопросы
        cursor.execute('SELECT "id_P_Question" FROM "Main"."P_Question" ORDER BY "id_P_Question" ASC ')
        select = cursor.fetchall()
        PQuesIdTuple = []
        for i in select:
            PQuesIdTuple.append(int(clear_str(str(i))))
        PQuestionsTable = []
        for i in PQuesIdTuple:
            cursor.execute(f""" select * from "Main"."P_Question" where "id_P_Question"={i} """)
            PQueSelect = cursor.fetchone()
            DBPQuestionId = PQueSelect[0]
            DBMainQuestionId = PQueSelect[1]
            DBPQuestion = PQueSelect[2]
            DBPAnswer = PQueSelect[3]
            DBPimg = PQueSelect[4]
            PQuestionsTable.append(list(map(str, f'{DBPQuestionId}|{DBMainQuestionId}|{DBPQuestion}|{DBPAnswer}|{DBPimg}'.split('|'))))
connect.close()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

Back = KeyboardButton('Назад')


@dp.message_handler(text='/start QA_Work', state='*')           # обработчик перехода по ссылке
async def initialize(message: types.Message):
    await state.State.set(States.mainMenu)
    CatRepKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    for i in CatIdTuple:                                                                    # Прохождение по строкам таблицы CategoryTable
        CatRepKeyboard.add(clear_str(CategoriesTable[i-1][1]))                                        # Добавление клавиш в клавиатуру
    await bot.send_message(chat_id=message.chat.id, text='Добро пожаловать в бота Москвариума.'
                                                         'В данном боте вы можете узнать ответы '
                                                         'на частые вопросы. Чтобы продолжить'
                                                         'выберите в нижней части экрана категорию вопроса',
                           reply_markup=CatRepKeyboard)


# Обработчик кнопки "Назад"
@dp.message_handler(text='Назад', state=States.Questions)
async def back_process(message: types.Message):
    await state.State.set(States.mainMenu)
    CatRepKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    for i in CatIdTuple:
        CatRepKeyboard.add(clear_str(CategoriesTable[i-1][1]))
    # Активация клавиатуры категорий
    await bot.send_message(chat_id=message.chat.id, reply_markup=CatRepKeyboard, text='Вы вернулись в меню категорий')


# Обработчик сообщений с клавиатур "Категории" и "Вопросы"
@dp.message_handler(content_types=['text'], state='*')
async def categories_handler(message: types.Message):
    await state.State.set(States.Questions)
    # Обработчик ввода категории
    for CategoriesId in CatIdTuple:                                                         # Прохождение по всем id категорий
        if message.text == CategoriesTable[CategoriesId-1][1]:                                        # Проверка категории
            QueRepKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            for QuesId in QuesIdTuple:                                                      # Прохождение по всем id вопросов
                QCategory = QuestionsTable[QuesId-1][1]
                if CategoriesId == int(QCategory):
                    QueRepKeyboard.add(QuestionsTable[QuesId-1][2])
            QueRepKeyboard.add(Back)
            await message.reply(text='Вопросы по данной категории:', reply_markup=QueRepKeyboard)
    # Обработчик ввода вопроса
    for QuesId in QuesIdTuple:
        if message.text == clear_str(QuestionsTable[QuesId-1][2]):
            keyboard_empty = True
            InlKeyboard = InlineKeyboardMarkup()
            for PQuesId in PQuesIdTuple:
                if int(clear_str(PQuestionsTable[PQuesId-1][1])) == QuesId:
                    button = InlineKeyboardButton(f'{PQuestionsTable[PQuesId-1][2]}', callback_data=f'button {PQuesId}')
                    InlKeyboard.add(button)
                    keyboard_empty = False
            if keyboard_empty:
                await bot.send_message(chat_id=message.chat.id, text=QuestionsTable[QuesId-1][3])
            else:
                await bot.send_message(chat_id=message.chat.id, text=QuestionsTable[QuesId-1][3],
                                       reply_markup=InlKeyboard)


@dp.callback_query_handler(text_startswith="button", state=States.Questions)        # Обработчик InlineKeyboard
async def check_callback(query: types.CallbackQuery):
    for PQuesId in PQuesIdTuple:
        if query.data == 'button ' + str(PQuesId):
            if PQuestionsTable[PQuesId-1][4] == 'None':
                await query.message.reply(text=PQuestionsTable[PQuesId-1][3])
            elif PQuestionsTable[PQuesId-1][4] != 'None':
                path = PQuestionsTable[PQuesId-1][4]
                await bot.send_photo(chat_id=query.message.chat.id, photo=open(path, 'rb'))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)