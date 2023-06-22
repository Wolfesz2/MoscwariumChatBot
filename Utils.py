from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(StatesGroup):
    mode = HelperMode.snake_case