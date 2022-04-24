from extra import get_cards
from models import Game, Player, Cards, Players, LocalCard
from photos import upload_photo
from vk_dark_library.VKBotLongPoll import user_or_chat, get_api
from vk_dark_library.VKCommandHandler import command_handler, search_command_handler

vk = get_api()


@command_handler("выйти")
def exit_game(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    player_id = Player.select().where(Player.user_id == kwargs["user_id"]).first().id
    if Players.select().where(Players.player_id == player_id).first() is None:
        vk.messages.send(**send_id, random_id=0,
                         message=f"Вы еще нигде не участвуете.")
        return
    game = Players.select().where(Players.player_id == player_id).first().game_id
    Players.delete().where(Players.player_id == player_id).execute()
    vk.messages.send(**send_id, random_id=0,
                     message=f"Вы вышли из игры. Ваш результат: {Player.select().where(Player.user_id == kwargs['user_id']).first().balls}")
    players = Players.select().where(Players.game_id == game)
    for one_player in players:
        vk.messages.send(user_id=one_player.player_id.user_id, message="Один из участников вышел.",
                         random_id=0)


@search_command_handler(["присоединиться", ' '])
def join_game(**kwargs):
    player = Player.get_or_create(user_id=kwargs["user_id"], defaults={"balls": 0})
    player[0].balls = 0
    player[0].voted = False
    player[0].save()
    send_id = user_or_chat(kwargs['raw'])
    player_id = Player.select().where(Player.user_id == kwargs["user_id"]).first().id
    if Players.select().where(Players.player_id == player_id).first() is not None:
        vk.messages.send(**send_id, random_id=0,
                         message=f"Вы уже участвуете в игре. Выйдите из нее командой 'выйти'")
        return
    if len(kwargs["splited"]) < 2:
        vk.messages.send(**send_id, random_id=0,
                         message=f"Для присоединения к игре нужно ввести ее ID. 'Присоединиться ID'")
        return
    game = Game.select().where(Game.id == kwargs["splited"][1]).first()
    if game is None:
        vk.messages.send(**send_id, random_id=0, message=f"Такой игры не найдено.")
        return
    players = Players.select().where(Players.game_id == kwargs["splited"][1])
    for one_player in players:
        vk.messages.send(user_id=one_player.player_id.user_id, message="К вам присоединился новый участник.",
                         random_id=0)
    cards = Cards.select().where(Cards.game_id == kwargs["splited"][1])
    ids = [i.number for i in cards]
    Players.create(game_id=kwargs["splited"][1], player_id=player[0].id)
    upload_photo(game.need_word, game.need_id, send_id, *ids)


def game_stop_local(win, raw, user_id):
    send_id = user_or_chat(raw)
    game = Game.select().where(Game.chief_id == user_id).first()
    if game is None:
        vk.messages.send(**send_id, random_id=0,
                         message=f"Вы еще не начали игру или не являетесь ее шефом.")
        return
    game_id = game.id
    players = Players.select().where(Players.game_id == game_id)
    Players.delete().where(Players.game_id == game_id).execute()
    Cards.delete().where(Cards.game_id == game_id).execute()
    LocalCard.delete().where(LocalCard.game_id == game_id).execute()
    game.delete_instance()
    text = f"Игра закончена. \nВы набрали: {Player.select().where(Player.user_id == user_id).first().balls} баллов\n"
    if win:
        text += "С победой :)"
    vk.messages.send(**send_id, random_id=0, message=text)
    for i in players:
        player = Player.select().where(Player.id == i.id).first()
        text = f"Игра закончена. \nВы набрали: {Player.select().where(Player.id == i.id).first().balls} баллов"
        if win:
            text += f"Победил @id{user_id}. Поздравим его. Игра окончена."
        vk.messages.send(user_id=player.user_id, random_id=0, message=text)


@command_handler("закончить")
def game_stop(**kwargs):
    game_stop_local(False, kwargs["raw"], kwargs["user_id"])


@command_handler("следующий")
def next_round(**kwargs):
    game = Game.select().where(Game.chief_id == kwargs["user_id"]).first()
    if game is None:
        vk.messages.send(user_id=kwargs["user_id"], random_id=0, message=f"Вы не шеф этого лобби.")
        return
    need_id, card_list, word = get_cards(game.id, kwargs["user_id"])
    game.need_id = need_id
    game.need_word = word
    game.save()
    Cards.delete().where(Cards.game_id == game.id).execute()
    player = Player.select().where(Player.user_id == kwargs["user_id"]).first()
    players = Players.select().where(Players.game_id == game.id)
    ids = [i.number for i in card_list]
    for i in players:
        player_local = Player.select().where(Player.id == i.player_id).first()
        player_local.voted = False
        player_local.save()
        if player_local.user_id == player.user_id:
            continue
        upload_photo(word, need_id, {"user_id": player_local.user_id}, *ids)
        vk.messages.send(user_id=player_local.user_id, random_id=0, message=f"Следующий раунд.")
    for i in card_list:
        cards = Cards(card_id=i.id, number=i.number, game_id=game.id)
        cards.save()


@command_handler("игры")
def all_games(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    games = Game.select()
    text = "Игры, проходящие сейчас:\n"
    if len(games) == 0:
        text += "Игр не найдено."
    for query in games:
        text += f"ID: {query.id}\n"
    vk.messages.send(**send_id, message=text, random_id=0)


@command_handler("результаты", "рейтинг")
def result(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    player = Player.select().where(Player.user_id == kwargs["user_id"]).first()
    game_id = Players.select().where(Players.player_id == player.id).first().game_id
    players = Players.select().where(Players.game_id == game_id)
    text = "Результаты этой игры:"
    for i in players:
        one_player = Player.select().where(Player.id == i.player_id).first()
        text += f"\n@id{one_player.user_id} - {one_player.balls} баллов"
    vk.messages.send(**send_id, message=text, random_id=0)


@command_handler("начать")
def game_start(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    game = Game.select().where(Game.chief_id == kwargs["user_id"]).first()
    if game is not None:
        vk.messages.send(**send_id, random_id=0,
                         message=f"Вы уже начали игру. Введите команду 'закончить' чтобы выйти.")
        return
    player = Player.get_or_create(user_id=kwargs["user_id"], defaults={"balls": 0})
    player[0].balls = 0
    player[0].voted = False
    player[0].save()
    game = Game.create(chief_id=kwargs["user_id"])
    need_id, card_list, word = get_cards(game.id, kwargs["user_id"])
    game.need_id = need_id
    game.need_word = word
    game.save()
    for i in card_list:
        cards = Cards(card_id=i.id, number=i.number, game_id=game.id)
        cards.save()
    players = Players(game_id=game.id, player_id=player[0].id)
    players.save()
    vk.messages.send(**send_id, random_id=0,
                     message=f"ID вашей игры - {game.id}.\nВаши друзья могут ввести команду 'Присоединиться {game.id}'")
