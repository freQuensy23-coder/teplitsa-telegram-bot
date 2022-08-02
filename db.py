from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_async_engine('sqlite+aiosqlite:///test.sqlite3', echo=True)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    course = Column(String)
    notification_mode = Column(Integer, default=1)  # 0 - all notifications, 1 - important, 2 - very important


async def get_or_create(async_sess, model, commit=True, **kwargs):
    async with async_sess() as sess:
        async with sess.begin():
            instance = await sess.execute(select(model).filter_by(**kwargs))
            if instance.first():
                return instance.first()
            else:
                instance = model(**kwargs)
                sess.add(instance)
                if commit:
                    await sess.commit()
                return instance


async def get_db_ready():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
