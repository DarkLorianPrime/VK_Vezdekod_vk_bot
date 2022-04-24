# -*- coding: utf-8 -*-
import os
import random

import requests
import sqlalchemy
from config import coloda
from models import Player, Game
from vk_dark_library.VKBotLongPoll import VKLongPoll, load_config, get_api, NEW, user_or_chat
from vk_dark_library.VKCommandHandler import CommandHandler, command_handler, search_command_handler

peoples = {}
load_config(os.getcwd(), "config")
vk = get_api()
images_ids = list(range(1, 99))


@command_handler("начать")
def games_list(**kwargs):
    player = Player(user_id=kwargs["user_id"], balls=0)
    game = Game(chief_id=kwargs["user_id"])
    game.players.append(player)


@command_handler("игры")
def games_list(**kwargs):
    pass


@search_command_handler(["присоединиться", ' '])
def join_game(**kwargs):
    pass


@command_handler("старт")
def start(**kwargs):
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
        CommandHandler().check_updates(vk_object)
        if peoples.get(str(vk_object.from_id)) is not None:
            print(peoples[str(vk_object.from_id)]["need_id"])
            if vk_object.text == peoples[str(vk_object.from_id)]["need_id"]:
                vk.messages.send(**send_id, message="Ты победил!", random_id=0)
