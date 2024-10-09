from aiogram.fsm.state import StatesGroup, State


class CreateContest(StatesGroup):
    CHOOSE_TITLE = State()  # Выбор названия викторины
    CHOOSE_DESCRIPTION = State()  # Выбор описания викторины
    ADD_QUESTIONS = State()  # Создание вопросов викторины
    FINISH_ADD_QUESTIONS = State()
    ADD_DOP_TEXT = State()
    FINISH = State()  # Подтверждение создания


class EditContest(StatesGroup):
    CHOOSE_ACTION = State()

    EDIT_TITLE = State()
    EDIT_DESCRIPTION = State()
    EDIT_QUESTIONS = State()
    EDIT_RESULTS = State()


class AddQuestion(StatesGroup):
    CHOOSE_DESCRIPTION = State() # Выбор описания вопроса
    ADD_VARIANTS = State()  # Добавление вариантов ответа
    CHOOSE_RIGHT = State()  # Выбор верного ответа
    FINISH = State()  # Подтверждение создания вопроса


class IDContest(StatesGroup):
    ENTER_ID = State()  # Ввод ID викторины
    CONTEST_COMPLETE = State()  # Процесс ответа на вопросы
    CONTEST_RESULT = State()  # Получения результатов прохождения
