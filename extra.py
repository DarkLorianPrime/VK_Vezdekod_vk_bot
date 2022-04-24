import random

from config import images_ids
from models import LocalCard
from photos import upload_photo
from vk_dark_library.VKBotLongPoll import user_or_chat


def get_cards(game_id, user_id):
    range_stop = 6
    ids = []
    card_list = []
    for i in range(0, range_stop):
        one_id = random.choice(images_ids)
        if one_id in ids:
            range_stop += 1
            continue
        ids.append(one_id)
        new_card = LocalCard(number=one_id, game_id=game_id)
        new_card.save()
        card_list.append(new_card)
        if len(ids) == 5:
            break
    need_id = -255
    while need_id == -255:
        need_id, word = upload_photo(None, None, {"user_id": user_id}, *ids)
    return need_id, card_list, word