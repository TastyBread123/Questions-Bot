from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.models import Contest, Question
from handlers.keyboards import add_qustions_kb, add_variants_kb, right_variant_kb
from utils.states import CreateContest, AddQuestion
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


router = Router()

@router.message(CreateContest.ADD_QUESTIONS)
async def add_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = await Question.filter(contest_id=int(data['contest_id'])).all()
    if len(questions) >= 10:
        return await message.answer('⚠️ В викторине не может быть больше 10 вопросов! Для продолжения нажмите на кнопку "✅ Дальше"')

    title = message.text.strip()
    if len(title) > 24:
        return await message.answer("⚠️ Длина названия вопроса не может быть больше 24 символов!")
    
    data.update({'title': title})
    await state.set_data(data)
    await message.answer("💥 Введите описание вопроса:")
    return await state.set_state(AddQuestion.CHOOSE_DESCRIPTION)


@router.message(AddQuestion.CHOOSE_DESCRIPTION)
async def question_description(message: types.Message, state: FSMContext):
    description = message.text.strip()
    if len(description) > 300:
        return await message.answer("⚠️ Длина описания вопроса не может быть больше 300 символов!")
    
    data = await state.get_data()
    contest = await Contest.get(id=data['contest_id'])
    question = await Question.create(contest=contest, title=data['title'], description=description)
    await question.save()

    variant_message = await message.answer(f"📌 Название: {data['title']}\n📔 Описание: {description}\n\n 💥 Вводите снизу варианты ответов (макс 8), для удаления нажмите на вариант ответа")
    await state.set_data({'contest_id': data['contest_id'], 'question_id': question.id, 'variant_message': variant_message, 'questions_message': data['questions_message'], 'variants': []})
    return await state.set_state(AddQuestion.ADD_VARIANTS)


@router.message(AddQuestion.ADD_VARIANTS)
async def question_variants(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if len(data['variants']) >= 8:
        return await message.answer('⚠️ Вы уже сделали 8 вариантов ответа, больше нельзя! Для продолжения нажмите на кнопку "✅ Дальше"')

    variant = message.text.strip()
    if len(variant) > 24:
        return await message.answer("⚠️ Длина варианта ответа не может быть больше 24 символов")
    
    if variant in data['variants']:
        return await message.answer("⚠️ У вас уже есть такой вариант ответа")

    data['variants'].append(variant)
    await state.set_data(data)

    kb = await add_variants_kb(data['question_id'], data['variants'])
    await data['variant_message'].edit_reply_markup(reply_markup=kb)
    
    return await message.reply(f"✅ Вариант {variant} успешно добавлен!")


@router.callback_query(AddQuestion.ADD_VARIANTS, F.data.startswith('delvariant_'))
async def del_variant_callback(call: types.CallbackQuery, state: FSMContext):
    _, question_id, variant_id = call.data.split("_")
    
    data = await state.get_data()
    data['variants'].pop(int(variant_id))
    await state.set_data(data)

    kb = await add_variants_kb(question_id, data['variants'])
    await call.message.edit_reply_markup(reply_markup=kb)


@router.callback_query(AddQuestion.ADD_VARIANTS, F.data.startswith("finish_variant_"))
async def finish_variants_create_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if len(data['variants']) <= 0:
        return await call.answer("❌ У вас нет вариантов для продолжения!", show_alert=True)

    question_id = int(call.data.strip("finish_variant_"))
    question = await Question.get(id=question_id)
    question.variants = data['variants']
    await question.save()

    await state.set_state(AddQuestion.CHOOSE_RIGHT)
    kb = await right_variant_kb(question_id)
    return await call.message.edit_text("🏆 Нажмите на вариант ответа, который будет считаться верным (макс 1)", reply_markup=kb)


@router.callback_query(AddQuestion.CHOOSE_RIGHT, F.data.startswith("rightvariant_"))
async def right_variant_callback(call: types.CallbackQuery, state: FSMContext):
    _, question_id, variant_id = call.data.split("_")
    question = await Question.get(id=int(question_id))
    question.right_variant = int(variant_id)
    await question.save()
    
    await state.set_state(AddQuestion.FINISH)
    variants = question.variants
    variants[question.right_variant] = f'✅ {variants[question.right_variant]}'
    variant_text = "\n".join(variants)

    FINISH_KB = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Готово', callback_data=f'finish_question_setting_{question_id}')]])
    return await call.message.edit_text(text=f'📌 Название вопроса: {question.title}\n📖 Описание: {question.description}\n\n🎓 Варианты ответов:\n{variant_text}\n\nВсё верно?', reply_markup=FINISH_KB)


@router.callback_query(AddQuestion.FINISH, F.data.startswith("finish_question_setting_"))
async def finish_question_setting_callback(call: types.CallbackQuery, state: FSMContext):
    # question_id = int(call.data.strip('finish_question_setting_'))

    await state.set_state(CreateContest.ADD_QUESTIONS)
    data = await state.get_data()
    await data['questions_message'].delete()
    
    kb = await add_qustions_kb(data['contest_id'])
    questions_message = await call.message.answer(text=data['questions_message'].text, reply_markup=kb)
    await state.set_data({'contest_id': data['contest_id'], 'questions_message': questions_message})
    return await call.message.delete()
