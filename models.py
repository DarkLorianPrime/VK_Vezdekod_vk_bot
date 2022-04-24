import os

from peewee import PostgresqlDatabase, Model, PrimaryKeyField, CharField, ForeignKeyField, IntegerField, BooleanField
import dotenv
dotenv.load_dotenv()

db = PostgresqlDatabase(os.getenv('DB'), user=os.getenv('USER'),
                        password=os.getenv('PASSWORD'),
                        host=os.getenv('HOST')
                        )


class BaseModel(Model):
    class Meta:
        database = db


class Game(BaseModel):
    id = PrimaryKeyField(null=False)
    chief_id = CharField(max_length=100)
    need_id = IntegerField(null=True)
    need_word = CharField(max_length=100, null=True)


class Player(BaseModel):
    id = PrimaryKeyField(null=False)
    user_id = CharField(max_length=100)
    balls = IntegerField()
    voted = BooleanField(default=False)


class LocalCard(BaseModel):
    id = PrimaryKeyField(null=False)
    number = IntegerField()
    game_id = IntegerField()


class Players(BaseModel):
    id = PrimaryKeyField(null=False)
    game_id = ForeignKeyField(Game)
    player_id = ForeignKeyField(Player)


class Cards(BaseModel):
    id = PrimaryKeyField(null=False)
    game_id = ForeignKeyField(Game)
    number = IntegerField()
    card_id = ForeignKeyField(LocalCard)


# Game.create_table()
# LocalCard.create_table()
# Player.create_table()
# Cards.create_table()
# Players.create_table()
