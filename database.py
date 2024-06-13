import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
load_dotenv()


class User(Base):
    __tablename__ = 'users'
    id = sq.Column(sq.Integer, primary_key=True)
    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.String)
    city = sq.Column(sq.String)
    photos = relationship('Photo', back_populates='user')


class Photo(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    url = sq.Column(sq.String)
    likes = sq.Column(sq.Integer)
    user = relationship('User', back_populates='photos')


class Favorite(Base):
    __tablename__ = 'favorites'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    favorite_user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    blacklisted_user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))


def get_top_three_photos_for_all_users(session):
    top_photos_query = text("""
    WITH RankedPhotos AS (
        SELECT *,
               RANK() OVER (PARTITION BY user_id ORDER BY likes DESC) as rank
        FROM photos
    )
    SELECT user_id, id, url, likes
    FROM RankedPhotos
    WHERE rank <= 3;
    """)
    result = session.execute(top_photos_query)
    return result.fetchall()


def create_session():
    DSN = os.getenv('DATABASE_URL')
    engine = create_engine(DSN)
    Session = sessionmaker(bind=engine)
    return Session()


# Создание таблиц в базе данных
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    DSN = os.getenv('DATABASE_URL')
    engine = create_engine(DSN)
    create_tables(engine)
    session = create_session()
    top_photos_for_all_users = get_top_three_photos_for_all_users(session)
    session.close()
