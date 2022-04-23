import os
import random
from itertools import islice

import requests

from vk_dark_library.VKBotLongPoll import VKLongPoll, load_config, get_api, NEW, user_or_chat
from vk_dark_library.VKCommandHandler import CommandHandler, command_handler, search_command_handler

load_config(os.getcwd(), "config")
vk = get_api()
user_dicts = {}
user_words = {}
images_ids = list(range(1, 99))


@command_handler("старт")
def start(**kwargs):
    send_id = user_or_chat(kwargs['raw'])
    server = vk.photos.getMessagesUploadServer(group_id=212876139)
    user_dicts[kwargs["user_id"]] = images_ids
    attachments = []
    cards_list = []
    for i in range(0, 5):
        one_id = random.choice(user_dicts[kwargs["user_id"]])
        user_dicts[kwargs["user_id"]].remove(one_id)
        with open(f"photos/{one_id}.jpg", "rb") as f:
            dr = requests.post(server['response']['upload_url'], files={'file1': f}).json()
        files = vk.photos.saveMessagesPhoto(**dr)
        cards_list.append(one_id)
        attachments.append(f'photo{files["response"][0]["owner_id"]}_{files["response"][0]["id"]}')
    words = []
    for int_id in cards_list:
        with open("photos/words.txt", "r") as file:
            for i, line in enumerate(file):
                if i - 1 == int_id:
                    words.append(line.split('\t')[1].split(" "))
    words = sum(words, [])
    words = set([i.replace("\n", "") for i in words])
    word = random.choice(list(words))
    vk.messages.send(**send_id, random_id=0, attachment=','.join(attachments))
    vk.messages.send(**send_id, random_id=0, message=f"Угадай номер картинки по слову {word}")


for vk_object in VKLongPoll().listen():
    if vk_object.type == NEW:
        CommandHandler().check_updates(vk_object)