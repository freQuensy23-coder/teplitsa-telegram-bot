from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///test.sqlite3?check_same_thread=False', echo=True) # TODO Что то придумать с проверкой потока в планировщике задач


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    course = Column(String)
    notification_mode = Column(Integer, default=1)  # 0 - all notifications, 1 - important, 2 - very important


def get_or_create(session, model, commit=True, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        if commit:
            session.commit()
        return instance


Base.metadata.create_all(engine)
