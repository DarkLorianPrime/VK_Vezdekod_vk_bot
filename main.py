# -*- coding: utf-8 -*-
import os
import random
import re

import requests
from config import coloda, images_ids
from models import Player, Game, Players
from vk_dark_library.VKBotLongPoll import VKLongPoll, load_config, get_api, NEW, user_or_chat

load_config(os.getcwd(), "config")
from vk_dark_library.VKCommandHandler import CommandHandler, command_handler
import main_functional

peoples = {}
vk = get_api()


@command_handler("старт")
def start(**kwargs):
    """100% DEPRECATED || 1-2 Task"""
    peoples[str(kwargs["user_id"])] = {"local_cards": images_ids, "need_id": 0}
    send_id = user_or_chat(kwargs['raw'])
    server = vk.photos.getMessagesUploadServer(group_id=212876139)
    attachments = []
    words = []
    id_words = {}
    for i in range(0, 5):
        one_id = random.choice(peoples[str(kwargs["user_id"])]["local_cards"])
        peoples[str(kwargs["user_id"])]["local_cards"].remove(one_id)
        with open(f"photos/{one_id}.jpg", "rb") as f:
            dr = requests.post(server['response']['upload_url'], files={'file1': f}).json()
        files = vk.photos.saveMessagesPhoto(**dr)
        words.append(coloda[str(one_id)].split(" "))
        id_words[str(one_id)] = coloda[str(one_id)].split(" ")
        attachments.append(f'photo{files["response"][0]["owner_id"]}_{files["response"][0]["id"]}')
    words = sum(words, [])
    word = random.choice(list(set([i.replace("\n", "") for i in words])))
    for k, v in id_words.items():
        if word in v:
            peoples[str(kwargs["user_id"])]["need_id"] = k
    vk.messages.send(**send_id, random_id=0, attachment=','.join(attachments))
    vk.messages.send(**send_id, random_id=0, message=f"Угадай номер картинки по слову {word}")


for vk_object in VKLongPoll().listen():
    if vk_object.type == NEW:
        send_id = user_or_chat(vk_object)
        if not CommandHandler().check_updates(vk_object):
            continue
        player = Player.select().where(Player.user_id == vk_object.from_id).first()
        if player.voted:
            vk.messages.send(**send_id, message="Вы не можете больше участвовать в этом раунде!", random_id=0)
            continue
        game_id = Players.select().where(Players.player_id == player.id).first()
        if game_id is None:
            continue
        game_id = game_id.game_id
        need_id = Game.select().where(Game.id == game_id).first().need_id
        if str(need_id) == vk_object.text.lower():
            vk.messages.send(**send_id, message="Совершенно верно!\n +3 балла этому господину!", random_id=0)
            if player.balls + 3 < 5:
                player.balls += 3
                player.voted = True
                player.save()
                continue
            main_functional.game_stop_local(True, vk_object, vk_object.from_id)
            continue
        vk.messages.send(**send_id, message="Не думаю что это верно!", random_id=0)
        player.voted = True
        player.save()
