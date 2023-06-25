import array
import aiogram.types
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import state
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
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

# todo: надо переделать все запросы так, чтобы они не зависели от ID
# todo: предполагаю, что это надо сделать через отдельный массив, где будут все ID
# todo: потом через for прогнать этот массив в селекте(примерно как на строках 43-45, только будет in массив)
# todo: можешь оставить это на меня
# todo: Если переделаешь, то надо весь код переделывать, ибо у меня весь код на MaxID основан
# todo: ниже еще задания, они легче: просто добавить State (чтобы работало все, если заруинишь, то я закибербулю тебя)

# Все выборки из базы данных
with connect:
    with connect.cursor() as cursor:
        # Категории
        cursor.execute('select max("id_Categories") from "Main"."Categories"')  # Выборка наибольшего Id
        MaxIdCat = cursor.fetchone()
        CategoryLen = int(clear_str(str(MaxIdCat)))
        CategoriesTable = []
        for i in range(CategoryLen):  # Построчная выборка всей таблицы
            cursor.execute(f""" select * from "Main"."Categories" where "id_Categories"={i + 1} """)
            CategorySelect = cursor.fetchone()
            DBCategoryId = CategorySelect[0]
            DBCategoryName = CategorySelect[1]
            # Добавление строк из таблицы Questions в массив CategoriesTable[строка][столбец]
            CategoriesTable.append(list(map(str, f'{DBCategoryId} {DBCategoryName}'.split())))
        # Вопросы
        cursor.execute('select max("id_Questions") from "Main"."Questions"')  # Выборка наибольшего Id
        MaxIdQuestion = cursor.fetchone()
        QuestionsLen = int(clear_str(str(MaxIdQuestion)))
        QuestionsTable = []
        for i in range(QuestionsLen):  # Построчная выборка всей таблицы
            cursor.execute(f""" select * from "Main"."Questions" where "id_Questions"={i + 1} """)
            QueSelect = cursor.fetchone()
            DBQuestionId = QueSelect[0]
            DBCategoryId = QueSelect[1]
            DBQuestion = QueSelect[2]
            DBAnswer = QueSelect[3]
            # Добавление строк из таблицы Questions в массив Questions[строка][столбец]
            QuestionsTable.append(list(map(str, f'{DBQuestionId} {DBCategoryId} {DBQuestion} {DBAnswer}'.split())))
        # Подвопросы
        cursor.execute('select max("id_P_Question") from "Main"."P_Question"')
        MaxIdPQuestions = cursor.fetchone()
        PQuestionsLen = int(clear_str(str(MaxIdPQuestions)))
        PQuestionsTable = []
        for i in range(PQuestionsLen):
            cursor.execute(f""" select * from "Main"."P_Question" where "id_P_Question"={i + 1} """)
            PQueSelect = cursor.fetchone()
            DBPQuestionId = PQueSelect[0]
            DBMainQuestionId = PQueSelect[1]
            DBPQuestion = PQueSelect[2]
            DBPAnswer = PQueSelect[3]
            DBPimg = PQueSelect[4]
            PQuestionsTable.append(list(map(str, f'{DBPQuestionId} {DBMainQuestionId} {DBPQuestion} {DBPAnswer} {DBPimg}'.split())))
connect.close()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

Back = KeyboardButton('Назад')


# todo: тут вообще желательно переделать текст ну и желательно проделать state, чтобы нельзя было найти бота в инете и ввести рандомно команду
@dp.message_handler(text='/start QA_Work')           # обработчик перехода по ссылке
async def initialize(message: types.Message):
    CatRepKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    for i in range(CategoryLen):                                                                    # Прохождение по строкам таблицы CategoryTable
        CatRepKeyboard.add(clear_str(CategoriesTable[i][1]))                                        # Добавление клавиш в клавиатуру
    await bot.send_message(chat_id=message.chat.id, text='Добро пожаловать в бота Москвариума.'
                                                         'В данном боте вы можете узнать ответы '
                                                         'на частые вопросы. Чтобы продолжить вы'
                                                         'выберите в нижней части экрана категорию вопроса',
                           reply_markup=CatRepKeyboard)


# todo: опять же state
# Обработчик кнопки "Назад"
@dp.message_handler(text='Назад')
async def back_process(message: types.Message):
    CatRepKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
    for i in range(CategoryLen):
        CatRepKeyboard.add(clear_str(CategoriesTable[i][1]))
    # Активация клавиатуры категорий
    await bot.send_message(chat_id=message.chat.id, reply_markup=CatRepKeyboard, text='Вы вернулись в меню категорий')


# todo: опять же state
# Обработчик сообщений с клавиатур "Категории" и "Вопросы"
@dp.message_handler(content_types=['text'])
async def categories_handler(message: types.Message):
    # Обработчик ввода категории
    for CategoriesId in range(CategoryLen):                                                         # Прохождение по всем id категорий
        if message.text == CategoriesTable[CategoriesId][1]:                                        # Проверка категории
            QueRepKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=10)
            for QuesId in range(QuestionsLen):                                                      # Прохождение по всем id вопросов
                QCategory = QuestionsTable[QuesId][1]
                if CategoriesId + 1 == int(QCategory):
                    QueRepKeyboard.add(QuestionsTable[QuesId][2])
            QueRepKeyboard.add(Back)
            await message.reply(text='Вопросы по данной категории:', reply_markup=QueRepKeyboard)
    # Обработчик ввода вопроса
    for QuesId in range(QuestionsLen):
        if message.text == clear_str(QuestionsTable[QuesId][2]):
            keyboard_empty = True
            InlKeyboard = InlineKeyboardMarkup()
            for PQuesId in range(PQuestionsLen):
                if int(clear_str(PQuestionsTable[PQuesId][1])) == QuesId+1:
                    button = InlineKeyboardButton(f'{PQuestionsTable[PQuesId][2]}', callback_data=f'button {PQuesId}')
                    InlKeyboard.add(button)
                    keyboard_empty = False
            if keyboard_empty:
                await bot.send_message(chat_id=message.chat.id, text=clear_str(QuestionsTable[QuesId][3]))
            else:
                await bot.send_message(chat_id=message.chat.id, text=clear_str(QuestionsTable[QuesId][3]),
                                       reply_markup=InlKeyboard)


# todo: опять же state
@dp.callback_query_handler(text_startswith="button")        # Обработчик InlineKeyboard
async def check_callback(query: types.CallbackQuery):
    for PQuesId in range(PQuestionsLen):
        if query.data == 'button ' + str(PQuesId):
            if PQuestionsTable[PQuesId][4] == 'None':
                await query.message.reply(text=PQuestionsTable[PQuesId][3])
            elif PQuestionsTable[PQuesId][4] != 'None':
                path = PQuestionsTable[PQuesId][4]
                await bot.send_photo(chat_id=query.message.chat.id, photo=open(path, 'rb'))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)