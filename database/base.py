from tortoise import Tortoise

async def init_database() -> None:
    await Tortoise.init(db_url='sqlite://db.sqlite3',
                        modules={'models': ['database.models']},
                        use_tz=False, timezone='Europe/Moscow',
                        )
    await Tortoise.generate_schemas()


async def close_database() -> None:
    await Tortoise.close_connections()
