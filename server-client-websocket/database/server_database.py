import asyncio
import os.path
from pathlib import Path

from sqlalchemy import Integer, String, DateTime, ForeignKey, func, Column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

path = Path(__file__).parent.resolve()
path_to_db = os.path.join(path, 'server_base.db')

Base = declarative_base()


class Clients(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    last_login = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'Client({self.id=}, {self.login=}, {self.last_login=})'

class ActiveClients(Base):
    __tablename__ = "active_clients"

    id = Column(Integer, primary_key=True)
    client_id = Column(ForeignKey('clients.id'), unique=True)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50))
    port = Column(String(50))


class ClientLoginHistory(Base):
    __tablename__ = "login_history"
    id = Column(Integer, primary_key=True)
    login = Column(ForeignKey('clients.login'))
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50))
    port = Column(String(50))


engine = create_async_engine(f"sqlite+aiosqlite:///{path_to_db}")
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)





