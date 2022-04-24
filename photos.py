import random

import requests

from config import coloda
from vk_dark_library.VKBotLongPoll import get_api

vk = get_api()


def upload_photo(word_primary=None, need_id_primary=None, send_id=None, *args):
    server = vk.photos.getMessagesUploadServer(group_id=212876139)
    words = []
    id_words = {}
    need_id = -255
    attachments = []
    for i in args:
        with open(f"photos/{i}.jpg", "rb") as f:
            dr = requests.post(server['response']['upload_url'], files={'file1': f}).json()
        uploaded_photo = vk.photos.saveMessagesPhoto(**dr)
        words.append(coloda[str(i)].split(" "))
        id_words[str(i)] = coloda[str(i)].split(" ")
        attachments.append(f'photo{uploaded_photo["response"][0]["owner_id"]}_{uploaded_photo["response"][0]["id"]}')
    print(send_id)
    vk.messages.send(**send_id, random_id=0, attachment=','.join(attachments))
    if word_primary is None:
        words = sum(words, [])
        word = random.choice(list(set([i.replace("\n", "") for i in words])))
        for k, v in id_words.items():
            if word in v:
                need_id = k
        vk.messages.send(**send_id, random_id=0, message=f"Угадай номер картинки по слову {word}")
        return need_id, word
    vk.messages.send(**send_id, random_id=0, message=f"Угадай номер картинки по слову {word_primary}")
    return need_id_primary, word_primary