from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from database.models import User, Contest, Question, Answer, Result
from aiogram.filters import Command
from utils.states import IDContest
from utils.keyboards import START_KB, CANCEL_KB, START_CONTEST_KB, variants_kb
from utils.get_results import get_results

router = Router()

@router.callback_query(F.data.startswith("contests_id"))
async def contests_id_callback(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state() != None:
        return await call.answer("Вы не можете использовать эту кнопку", show_alert=True)
    
    await call.message.edit_text("✍️ Введите ID викторины ниже", reply_markup=CANCEL_KB)
    return await state.set_state(IDContest.ENTER_ID)


@router.callback_query(IDContest.ENTER_ID, F.data.startswith("cancel"))
async def cancel_enter_id_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    return await call.message.edit_text(text="👋 Привет! Ты попал в бота для создания и прохождения викторин. Все доступные действия ты можешь видеть на кнопках снизу. Приятного пользования!", reply_markup=START_KB)


@router.message(IDContest.ENTER_ID)
async def enter_id_handler(message: types.Message, state: FSMContext, payload_start: str = None):
    data = await state.get_data()
    if not data.get("contest_message") is None:
        await data['contest_message'].edit_reply_markup(reply_markup=None)

    contest_id = message.text.strip()
    if not payload_start is None:
        contest_id = payload_start

    if not contest_id.isdigit():
        return await message.reply("❌ ID викторины должен быть числом!")
    
    contest = await Contest.get_or_none(id=contest_id)
    if contest is None:
        return await message.reply("❌ Викторина с таким ID не найдена!")
    
    questions = await Question.filter(contest=contest).all()
    contest_message = await message.reply(text=f'📋 Информация по викторине "{contest.title}" (ID {contest.id})\n❓ Количество вопросов: {len(questions)}\n📌Описание: {contest.description}\n\nГотовы начать?', reply_markup=START_CONTEST_KB)
    return await state.set_data({'contest_message': contest_message, 'contest': contest, 'questions': questions, 'current_question': 1})


@router.callback_query(IDContest.ENTER_ID, F.data.startswith("start_enter_id"))
async def start_enter_id_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(IDContest.CONTEST_COMPLETE)
    current_question = data['questions'][0]

    kb = await variants_kb(current_question)
    await call.message.edit_text(f"Вопрос {data['current_question']} / {len(data['questions'])}\n\n❔ {current_question.title}\n📖 {current_question.description}\n\nВыберите ответ ниже:", reply_markup=kb)


@router.callback_query(IDContest.CONTEST_COMPLETE, F.data.startswith("variant_"))
async def variant_callback(call: types.CallbackQuery, state: FSMContext):
    variant = int(call.data.strip("variant_"))

    data = await state.get_data()
    current_question = data['questions'][data['current_question'] - 1]
    user = await User.get(id=call.from_user.id)
    await Answer.create(question=current_question, variant=variant, is_right=variant==current_question.right_variant, creator=user)

    if data['current_question'] >= len(data['questions']):
        return await results(call, state)

    data['current_question'] += 1
    await state.set_data(data)

    current_question = data['questions'][data['current_question'] - 1]
    kb = await variants_kb(current_question)
    await call.message.edit_text(f"Вопрос {data['current_question']} / {len(data['questions'])}\n\n❔ {current_question.title}\n📖 {current_question.description}\n\nВыберите ответ ниже:", reply_markup=kb)



async def results(call: types.CallbackQuery, state: FSMContext):
    # Функция подсчёта результатов

    data = await state.get_data()
    user = await User.get(id=call.from_user.id)

    questions_quant = len(data['questions'])
    right_answers = len((await Answer.filter(creator=user, is_right=True).all()))
    percent = round(right_answers / questions_quant * 100)
    dop_text = get_results(data['contest'].dop_texts, percent)

    # await Result.create(user=user, contest=data['contest'], right_answers=right_answers, all_answers=questions_quant, dop_text=result)
    await Answer.filter(creator=user).delete()

    return await call.message.edit_text(f"🏆 Вы успешно прошли викторину!\n❔ Процент прохождения - {percent}%\n💬 Результат: {dop_text}", reply_markup=None)
