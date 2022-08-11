import asyncio
import os
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.server_db_utils import ServerStorage

path = Path(__file__).parent.resolve()
path_to_db = os.path.join(path, 'server_base_test.db')

engine = create_async_engine(f"sqlite+aiosqlite:///{path_to_db}")
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def async_main():
    test_db = ServerStorage(async_session, engine_cls=engine)
    await test_db.init_db()

    await test_db.register_client('client_1', '192.168.1.4', 8080)
    await test_db.register_client('client_2', '192.168.1.5', 7777)

    # Выводим список кортежей - активных пользователей
    print(' ---- test_db.active_users_list() ----')
    print(await test_db.active_users_list())

    # Выполняем "отключение" пользователя
    await test_db.user_logout('client_1')
    # И выводим список активных пользователей
    print(' ---- test_db.active_users_list() after logout client_1 ----')
    print(await test_db.active_users_list())

    # Запрашиваем историю входов по пользователю
    print(' ---- test_db.login_history(client_1) ----')
    print(await test_db.login_history('client_1'))

    # и выводим список известных пользователей
    print(' ---- test_db.users_list() ----')
    print(await test_db.users_list())


asyncio.run(async_main())
