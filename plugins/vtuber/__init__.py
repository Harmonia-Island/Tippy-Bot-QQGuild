import json
import os
import time
import random

from configs.path import TXT_PATH
from typing import Optional
from utils.http_utils import AsyncAioHTTP


def get_vtubers(seed=None, return_type: Optional[str] = 'classic'):
    if seed:
        random.seed(seed)
    if random.random() > 0.96:
        with open(TXT_PATH / 'vtbs_addon.json', 'r', encoding="utf8") as vj:
            _ad = json.load(vj)
    else:
        with open(TXT_PATH / 'vtbs.json', 'r', encoding="utf8") as vj:
            _ad = json.load(vj)

    _choice = random.choice(_ad)
    if return_type == 'classic':
        _uname = _choice['uname']
        _sign = _choice['sign']
        _face = _choice['face']
        _fo = _choice['follower']
        _gn = _choice['guardNum']
        _video = _choice['video']
        _room = _choice['roomid']
        _announce = _choice['notice']
        vtb = f'\n今日推荐Vtuber: {_uname}\n'
        vtb2 = f"\n粉丝数: {_fo}\n"\
                + f"总投稿数: {_video}\n"\
                + f"舰长数: {_gn}\n"\
                + f"简介: {_sign}\n"\
                + f"公告: {_announce}\n"\
                + f"主页: https://space.bilibili.com/{_choice['mid']}\n"\
                + f"直播间: https://live.bilibili.com/{_room}"
        return (vtb, vtb2, _face)
    elif return_type == 'dict':
        return _choice
    else:
        return None