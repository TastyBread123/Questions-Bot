from handlers.commands.start import router as start_router
from handlers.commands.profile import router as profile_router
from handlers.commands.create_contest.create_contest import router as cr_contest_router
from handlers.commands.create_contest.create_question import router as cr_question_router
from handlers.commands.play_contest.id_enter import router as id_enter_router

routers = [start_router, profile_router, cr_contest_router, cr_question_router, id_enter_router]
