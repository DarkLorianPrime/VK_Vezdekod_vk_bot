import os

from sqlalchemy import Integer, Column, String, Table, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
import dotenv

Base = declarative_base()

Players = Table("players",
                Base.metadata,
                Column('id', Integer, primary_key=True),
                Column('game_id', Integer, ForeignKey('game.id')),
                Column('player_id', Integer, ForeignKey('player.id')))

Cards = Table("card",
              Base.metadata,
              Column('id', Integer, primary_key=True),
              Column('game_id', Integer, ForeignKey('game.id')),
              Column('card_id', Integer, ForeignKey('card.id')))


class Game(Base):
    __tablename__ = "game"
    id = Column(Integer, primary_key=True)
    chief_id = Column(String(100), nullable=False)
    players = relationship('Player', secondary=Players, backref='players_game')
    cards = relationship('LocalCard', secondary=Cards, backref='cards_game')
    need_id = Column(Integer, nullable=False)


class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    balls = Column(Integer, nullable=False)


class LocalCard(Base):
    __tablename__ = "localcard"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)


def get_db():
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('USER')}:{os.getenv('PASSWORD')}@{os.getenv('HOST')}/{os.getenv('DB')}")
    engine.connect()
    return Session(bind=engine)


dotenv.load_dotenv()
for i in range(1, 99):
    lcs = LocalCard(number=i)
db = get_db()
db.add(lcs)
db.commit()
