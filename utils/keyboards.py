from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.models.question import Question


START_KB = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🆔 Войти по ID', callback_data='contests_id')], [InlineKeyboardButton(text='✏️ Создать викторину', callback_data='contests_create')]])
START_CONTEST_KB = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_enter_id')], [InlineKeyboardButton(text='✅ Начать', callback_data='start_enter_id')]])
CANCEL_KB = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]])
FINISH_CREATE_CONTEST_KB = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Да', callback_data='finish_create_contest')], [InlineKeyboardButton(text='❌ Нет', callback_data='cancel_finish_create_contest')]])
SKIP_DOP_TEXT_CREATE = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='▶️ Пропустить', callback_data='skip_dop_text')]])
BACK_TO_MAIN_MENU = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Вернуться в главное меню")]])


async def add_qustions_kb(contest_id: int):
    kb = [[InlineKeyboardButton(text='✅ Дальше', callback_data=f'finish_questions_{contest_id}')]]
    questions = await Question.filter(contest_id=contest_id).all()

    for question in questions:
        kb.append([InlineKeyboardButton(text=question.title, callback_data=f'edit_question_{question.id}')])

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def add_variants_kb(question_id: int, variants: list = None):
    kb = [[InlineKeyboardButton(text='✅ Дальше', callback_data=f'finish_variant_{question_id}')]]

    for variant in variants:
        kb.append([InlineKeyboardButton(text=variant, callback_data=f'delvariant_{question_id}_{variants.index(variant)}')])

    return InlineKeyboardMarkup(inline_keyboard=kb)

async def right_variant_kb(question_id: int):
    question = await Question.get(id=question_id)

    kb = []
    for variant in question.variants:
        kb.append([InlineKeyboardButton(text=variant, callback_data=f'rightvariant_{question_id}_{question.variants.index(variant)}')])

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def variants_kb(question: Question):
    kb = []
    for variant in question.variants:
        kb.append([InlineKeyboardButton(text=variant, callback_data=f'variant_{question.variants.index(variant)}')])

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def results_kb(contest_id: int, results: dict):
    kb = [[InlineKeyboardButton(text='✅ Дальше', callback_data=f'finish_results_{contest_id}')]]
    
    for i in results:
        text = results[i]
        if len(text) >= 32:
            text = text[:30] + '...'

        kb.append([InlineKeyboardButton(text=f'{i}% - {text}', callback_data=f'delete_result_{i}')])

    return InlineKeyboardMarkup(inline_keyboard=kb)
