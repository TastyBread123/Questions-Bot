from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from database.models import Contest, User
from utils.states import CreateContest
from utils.keyboards import CANCEL_KB, START_KB, FINISH_CREATE_CONTEST_KB, SKIP_DOP_TEXT_CREATE, add_qustions_kb, results_kb

router = Router()

@router.callback_query(F.data.startswith("contests_create"))
async def contests_create_callback(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state() != None:
        return await call.answer("Вы не можете использовать эту кнопку", show_alert=True)
    
    await call.answer()
    await User.get_or_create(id=call.from_user.id)
    await call.message.edit_text("💥 Введите название викторины:", reply_markup=CANCEL_KB)
    return await state.set_state(CreateContest.CHOOSE_TITLE)


@router.callback_query(CreateContest.CHOOSE_TITLE, F.data.startswith("cancel"))
async def cancel_create_contest_callback(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    return await call.message.edit_text(text="👋 Привет! Ты попал в бота для создания и прохождения викторин. Все доступные действия ты можешь видеть на кнопках снизу. Приятного пользования!", reply_markup=START_KB)


@router.message(CreateContest.CHOOSE_TITLE)
async def choose_title_create_contest(message: types.Message, state: FSMContext):
    title = message.text.strip()
    if len(title) > 32:
        return await message.answer("⚠️ Длина названия не может быть больше 32 символов")
    
    await state.set_data({"title": title})
    await message.answer("💥 Введите описание викторины:")
    return await state.set_state(CreateContest.CHOOSE_DESCRIPTION)


@router.message(CreateContest.CHOOSE_DESCRIPTION)
async def choose_description_create_contest(message: types.Message, state: FSMContext):
    description = message.text.strip()
    if len(description) > 300:
        return await message.answer("⚠️ Длина описания не может быть больше 300 символов")
    
    info = await state.get_data()
    await state.clear()
    await state.set_state(CreateContest.ADD_QUESTIONS)
    
    creator = await User.get(id=message.from_user.id)
    contest = await Contest.create(creator=creator, title=info['title'], description=description)
    await contest.save()
    
    questions_message = await message.answer(f"📌 Название: {info['title']}\n📔 Описание: {description}\n\n❓ Введите название нового вопроса для его создания")
    await state.set_data({'contest_id': contest.id, 'questions_message': questions_message})


@router.callback_query(CreateContest.ADD_QUESTIONS, F.data.startswith("finish_questions_"))
async def finish_questions_calback(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateContest.FINISH_ADD_QUESTIONS)
    return await call.message.edit_text("🧐 Вы уверены, что готовы завершить настройку вопросов викторины?", reply_markup=FINISH_CREATE_CONTEST_KB)


@router.callback_query(CreateContest.FINISH_ADD_QUESTIONS, F.data.__eq__("cancel_finish_create_contest"))
async def cancel_finish_create_contest_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(CreateContest.ADD_QUESTIONS)

    kb = await add_qustions_kb(data['contest_id'])
    questions_message = await call.message.edit_text(text=data['questions_message'].text, reply_markup=kb)
    return await state.set_data({'contest_id': data['contest_id'], 'questions_message': questions_message})


@router.callback_query(CreateContest.FINISH_ADD_QUESTIONS, F.data.__eq__("finish_create_contest"))
async def finish_create_questions_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message = await call.message.edit_text("📚 Введите результаты прохождения викторины в формате: процент прохождения - реузльтат\nПример: 55 - молодец, но можно лучше!\n\n❗️ Если вы сделаете только 1 результат, он будет отбражаться в любом случае", reply_markup=SKIP_DOP_TEXT_CREATE)
    data.update({'dop_texts': {}, 'results_message': message})

    await state.set_data(data)
    return await state.set_state(CreateContest.ADD_DOP_TEXT)


@router.callback_query(CreateContest.ADD_DOP_TEXT, F.data.__eq__("skip_dop_text"))
async def skip_dop_text_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    contest = await Contest.get(id=data['contest_id'])
    contest.dop_texts = {'-1': 'Благодарим за прохождение!'}
    await contest.save()
    await state.set_state(CreateContest.FINISH)
    return await call.message.edit_text("🧐 Вы уверены, что готовы пропустить настройку результатов викторины?", reply_markup=FINISH_CREATE_CONTEST_KB)


@router.message(CreateContest.ADD_DOP_TEXT)
async def add_dop_text_handler(message: types.Message, state: FSMContext):
    result = message.text.strip().split("-", maxsplit=1)
    if len(result) != 2:
        return await message.reply("⚠️ Текст должен быть в следуюзем формате: процент прохождения - реузльтат\nПример: 55 - молодец, но можно лучше!")

    percent = result[0].strip()
    if not percent.isdigit() or int(percent) < 0:
        return await message.reply("⚠️ Процент прохождения должен быть числом большим или равным 0")

    text = result[1].strip()
    if len(text) > 500 or len(text) <= 0:
        return await message.reply("⚠️ Результат не может быть длиннее 500 символов или меньше 1 символа")
    
    data = await state.get_data()
    data['dop_texts'].update({percent: text})

    kb = await results_kb(data['contest_id'], data['dop_texts'])
    results_message = await message.answer(data['results_message'].text, reply_markup=kb)
    await data['results_message'].delete()
    data['results_message'] = results_message
    return await state.set_data(data)


@router.callback_query(CreateContest.ADD_DOP_TEXT, F.data.startswith('delete_result_'))
async def delete_result_create_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    var = call.data.strip('delete_result_')

    data['dop_texts'].pop(var)
    await state.set_data(data)

    kb = await results_kb(data['contest_id'], data['dop_texts'])
    return await call.message.edit_reply_markup(reply_markup=kb)


@router.callback_query(CreateContest.ADD_DOP_TEXT, F.data.startswith("finish_results_"))
async def finish_results_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    contest_id = int(call.data.strip("finish_results_"))
    contest = await Contest.get(id=contest_id)
    contest.dop_texts = data['dop_texts']
    await contest.save()

    await state.set_state(CreateContest.FINISH)
    return await call.message.edit_text("🧐 Вы уверены, что готовы завершить настройку результатов викторины?", reply_markup=FINISH_CREATE_CONTEST_KB)


@router.callback_query(CreateContest.FINISH, F.data.__eq__("cancel_finish_create_contest"))
async def cancel_finish_create_contest_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    kb = SKIP_DOP_TEXT_CREATE
    if len(data['dop_texts']) > 0:
        kb = await results_kb(data['contest_id'], data['dop_texts'])

    results_message = await call.message.edit_text(text=data['results_message'].text, reply_markup=kb)
    data.update({'results_message': results_message})
    await state.set_data(data)
    return await state.set_state(CreateContest.ADD_DOP_TEXT)


@router.callback_query(CreateContest.FINISH, F.data.__eq__("finish_create_contest"))
async def finish_create_contest_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    contest = await Contest.get(id=int(data['contest_id']))
    contest.active = True
    await contest.save()
    await state.clear()

    link = await create_start_link(call.bot, contest.id)
    return await call.message.edit_text(f'😏 Вы успешно создали викторину "{contest.title}" (ID {contest.id})\n💬 Ссылка для друзей: {link}', reply_markup=None)
