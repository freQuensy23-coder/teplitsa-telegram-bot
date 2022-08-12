import sqlalchemy.exc
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref

Base = declarative_base()
engine = create_engine('sqlite:///test.sqlite3?check_same_thread=False',
                       echo=True)  # TODO Что то придумать с проверкой потока для планировщика задач

course_tag = Table('course_tag', Base.metadata,
                   Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
                   Column('course_id', Integer, ForeignKey('course.id'), primary_key=True))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    courses = relationship('Course', secondary=course_tag, backref=backref('course_tag'))
    notification_mode = Column(Integer, default=1)  # 0 - all notifications, 1 - important, 2 - very important


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    

def get_course_by_name(session, name):
    return session.query(Course).filter_by(name=name).first()


def get_all_courses(session=None):
    if session is None:
        session = sessionmaker(bind=engine)()
    return session.query(Course).all()


def get_or_create(session=None, model=None, commit=True, create=True, **kwargs):
    """Получить модель model через сессию session. Если модель не найдена и указан флаг create, то создать ее и
    вернуть ее. Если commit за обновить базу. """
    if session is None:
        session = sessionmaker(bind=engine)()
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    elif create:
        instance = model(**kwargs)
        session.add(instance)
        if commit:
            session.commit()
        return instance
    raise sqlalchemy.exc.NoResultFound()

Base.metadata.create_all(engine)

if __name__ == "__main__":
    course = get_or_create(model=Course, name='Test course 1', description='Python course')
