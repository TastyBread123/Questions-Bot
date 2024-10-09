from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.models import User, Answer, Contest
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject

from utils.keyboards import START_KB, BACK_TO_MAIN_MENU
from utils.states import IDContest
from handlers.commands.play_contest.id_enter import enter_id_handler


router = Router()

@router.message(CommandStart(deep_link=True))
async def start_cmd_deep(message: types.Message, state: FSMContext, command: CommandObject):
    args = command.args

    await state.clear()
    user = (await User.get_or_create(id=message.from_user.id))[0]
    answers = await Answer.filter(creator=user).all()
    if len(answers) > 0:
        await Answer.filter(creator=user).all().delete()
    
    contest = await Contest.get_or_none(id=args)
    if contest is None:
        return await message.reply("⛔️ Произошла ошибка! Вы можете вернуться в главное меню, нажав на кнопку ниже", reply_markup=BACK_TO_MAIN_MENU)
    
    await state.set_state(IDContest.ENTER_ID)
    return await enter_id_handler(message=message, state=state, payload_start=args)


@router.message(CommandStart(ignore_case=True))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()

    user = (await User.get_or_create(id=message.from_user.id))[0]
    answers = await Answer.filter(creator=user).all()
    if len(answers) > 0:
        await Answer.filter(creator=user).all().delete()
    
    return await message.answer("👋 Привет! Ты попал в бота для создания и прохождения викторин. Все доступные действия ты можешь видеть на кнопках снизу. Удачи!", reply_markup=START_KB)
