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
from Config import TOKEN
from Utils import States

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(text='/start ml10')
async def initialize(message: types.Message):

    rpl_keyboard =
    await bot.send_message(chat_id=message.chat.id, text='Добро пожаловать в бота Москвариума.'
                                                         'В данном боте вы можете узнать ответы '
                                                         'на частые вопросы.', reply_markup=rpl_keyboard)
    
    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)