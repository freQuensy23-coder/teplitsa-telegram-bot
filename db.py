from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine('memory://')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    course = Column(String)
    notification_mode = Column(Integer)  # 0 - all notifications, 1 - important, 2 - very important


def get_or_create(sess, model, **kwargs):
    instance = sess.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        sess.add(instance)
        sess.commit()
        return instance
