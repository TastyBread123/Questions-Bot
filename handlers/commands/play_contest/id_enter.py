from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from database.models import User, Contest, Question, Answer, Result
from aiogram.filters import Command
from utils.states import IDContest
from handlers.keyboards import START_KB, restart_contest_kb, start_contest_kb, BACK_KB, variants_kb
from utils.get_results import get_results

router = Router()

@router.callback_query(F.data.startswith("contests_id"))
async def contests_id_callback(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state() != None:
        return await call.answer("Вы не можете использовать эту кнопку", show_alert=True)
    
    await call.message.edit_text("✍️ Введите ID викторины ниже. Его вам может предоставить создатель викторины", reply_markup=BACK_KB)
    return await state.set_state(IDContest.ENTER_ID)


@router.message(IDContest.ENTER_ID)
async def enter_id_handler(message: types.Message, state: FSMContext, payload_start: str = None):
    contest_id = message.text.strip()
    if not payload_start is None:
        contest_id = payload_start

    if not contest_id.isdigit():
        return await message.reply("❌ ID викторины должен быть числом не меньше 0!")
    
    contest = await Contest.get_or_none(id=contest_id)
    if contest is None:
        return await message.reply("❌ Викторина с таким ID не найдена! Проверьте правильность написания")
    
    questions = await Question.filter(contest=contest).count()
    return await message.reply(text=f'📋 <b>{contest.title}</b> (ID {contest.id})\n<b>❓ Вопросов</b>: {questions}\n📌 <b>Описание</b>: {contest.description}\n\n<b>🚀 Готовы начать?</b>', reply_markup=start_contest_kb(contest.id), parse_mode='HTML')


@router.callback_query(F.data.startswith("start_enter_id-"))
async def start_enter_id_callback(call: types.CallbackQuery, state: FSMContext):
    user = (await User.get_or_create(id=call.from_user.id))[0]
    if user.current_contest != None:
        return await call.answer("Сначала завершите участие в предыдущей викторине!")
    
    contest_id = int(call.data.split('-', maxsplit=1)[-1])
    data = await state.get_data()
    await state.set_state(IDContest.CONTEST_COMPLETE)

    contest = await Contest.get_or_none(id=contest_id)
    questions = await Question.filter(contest=contest).all()
    await state.set_data({'contest_message': call.message, 'contest': contest, 'questions': questions, 'current_question': 1})
    data = await state.get_data()

    user.current_contest = contest.id
    await user.save()

    current_question = questions[0]
    kb = await variants_kb(current_question)
    await call.message.edit_text(f"❔ Вопрос {data['current_question']} / {len(data['questions'])}\n\n📖 <b>{current_question.title}</b>\n<i>{current_question.description}</i>", reply_markup=kb, parse_mode='HTML')


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
    await call.message.edit_text(f"❔ Вопрос {data['current_question']} / {len(data['questions'])}\n\n📖 <b>{current_question.title}</b>\n<i>{current_question.description}</i>", reply_markup=kb, parse_mode='HTML')


async def results(call: types.CallbackQuery, state: FSMContext):
    # Функция подсчёта результатов

    user = await User.get(id=call.from_user.id)
    user.current_contest = None
    await user.save()

    data = await state.get_data()
    questions_quant = len(data['questions'])
    right_answers = len((await Answer.filter(creator=user, is_right=True).all()))
    percent = round(right_answers / questions_quant * 100)
    dop_text = get_results(data['contest'].dop_texts, percent)

    # await Result.create(user=user, contest=data['contest'], right_answers=right_answers, all_answers=questions_quant, dop_text=result)
    await Answer.filter(creator=user).delete()

    return await call.message.edit_text(f"🏆 Вы завершили викторину!\n\n❔ Процент прохождения - {percent}%\n💬 Результат: {dop_text}", reply_markup=restart_contest_kb(data['contest'].id))
