from sqlalchemy import select, func

from database.server_database import Clients, engine, Base, ActiveClients, ClientLoginHistory


# Класс - серверная база данных:
class ServerStorage:
    def __init__(self, session, engine_cls=engine):
        self.async_session = session
        self.engine = engine_cls

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Функция выполняющаяся при входе пользователя, записывает в базу факт входа
    async def register_client(self, login, ip_address, port):
        """
        Функция регистрация пользователя в безе данных
        """
        async with self.async_session() as session:
            # Получаем пользователя по логину
            result = await session.execute(select(Clients).where(Clients.login == login))
            user: Clients = result.scalars().first()

            # Если пользователя нет, его в базу данных
            if not user:
                user = Clients(login=login)
                session.add(user)
                await session.commit()

            # Если пользователь есть, обновляем время его последнего логина
            else:
                user.last_login = func.now()
                await session.commit()

            # Теперь можно создать запись в таблицу активных пользователей о факте входа.
            # Создаём экземпляр класса ActiveClients, через который передаём данные в таблицу
            new_active_user = ActiveClients(client_id=user.id, ip_address=ip_address, port=port)
            session.add(new_active_user)

            # Создаём экземпляр класса self.LoginHistory, через который передаём данные в таблицу
            history = ClientLoginHistory(login=user.login, ip_address=ip_address, port=port)
            session.add(history)

            await session.commit()

    async def user_logout(self, login):
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы self.AllUsers
        async with self.async_session() as session:
            result = await session.execute(select(Clients).where(Clients.login == login))
            user: Clients = result.scalars().first()
            # Удаляем его из таблицы активных пользователей.
            # Удаляем запись из таблицы ActiveClients
            result_active = await session.execute(select(ActiveClients).where(ActiveClients.client_id == user.id))
            user_active = result_active.scalars().first()

            await session.delete(user_active)
            await session.commit()

    # Функция возвращает список известных пользователей со временем последнего входа.
    async def users_list(self):
        # Запрос строк таблицы пользователей.
        async with self.async_session() as session:
            result = await session.execute(select(
                Clients.login,
                Clients.last_login
            ))
            # Возвращаем список кортежей
            return result.fetchall()

    # Функция возвращает список активных пользователей
    async def active_users_list(self):
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        async with self.async_session() as session:
            result = await session.execute(select(
                Clients.login,
                ActiveClients.ip_address,
                ActiveClients.port,
                ActiveClients.login_time
            ).join(Clients))
            # Возвращаем список кортежей
            return result.fetchall()

    async def login_history(self, login=None):

        async with self.async_session() as session:
            # Запрашиваем историю входа
            stmt = select(Clients.login,
                          ClientLoginHistory.login_time,
                          ClientLoginHistory.ip_address,
                          ClientLoginHistory.port
                          ).join(Clients)

            if login:
                result = await session.execute(stmt.where(Clients.login == login))
            else:
                result = await session.execute(stmt)
            # Если было указано имя пользователя, то фильтруем по этому имени

        # Возвращаем список кортежей
        return result.fetchall()
