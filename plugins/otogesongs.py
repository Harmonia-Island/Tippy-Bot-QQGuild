from io import BytesIO
from typing import Union

from botpy import BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message
from utils.utils import text_to_image

from .arcaea import get_arcaea_songs
from .arcaea import total_list as arcaea_total_list
from .bangdream import generate_gbp_graph
from .bangdream import total_list as bang_dream_total_list
from .lovelive import get_sif_songs
from .lovelive import total_list as ll_total_list
from .maimaidx import generate_music_graph_new
from .maimaidx import total_list as maimai_total_list
from .maimaidx import total_list_jp as universe_total_list
from .chunithm import generate_chuni_graph_new, chuni_music_list
from .pjsk import (generate_sekai_music_graph)
from .pjsk import total_list as sekai_total_list


def search_handler(keyword, whitelisted=False) -> Union[bytes, str]:
    ttl_len = 0
    # 舞萌DX search
    if isinstance(keyword, list):
        kws = keyword
    else:
        kws = [keyword]
    res_wm = []
    res_arc = []
    res_uni = []
    res_chuni = []
    res_gbp = []
    res_ll = []
    res_pjsk = []

    for kw in kws:
        _res_wm = maimai_total_list.filter(title_search=kw)
        [res_wm.append(x) for x in _res_wm if x not in res_wm]
        ttl_len += len(_res_wm)

        # maimai DX search
        if whitelisted:
            _res_uni = universe_total_list.filter(title_search=kw)
        else:
            _res_uni = universe_total_list.filter(title_search='1145141919810')
        [res_uni.append(x) for x in _res_uni if x not in res_uni]
        ttl_len += len(_res_uni)

        # Chunithm NEW search
        _res_chuni = chuni_music_list.filter(title_search=kw)
        [res_chuni.append(x) for x in _res_chuni if x not in res_chuni]
        ttl_len += len(_res_chuni)

        # BanG Dream search
        _res_gbp = bang_dream_total_list.filter(title_search=kw)
        [res_gbp.append(x) for x in _res_gbp if x not in res_gbp]
        ttl_len += len(_res_gbp)

        # Project Sekai search
        _res_pjsk = sekai_total_list.filter(title_search=kw)
        [res_pjsk.append(x) for x in _res_pjsk if x not in res_pjsk]
        ttl_len += len(_res_pjsk)

        # LoveLive search
        _res_ll = ll_total_list.filter(title_search=kw)
        [res_ll.append(x) for x in _res_ll if x not in res_ll]
        ttl_len += len(_res_ll)

        # Arcaea search
        _res_arc = arcaea_total_list.filter(title_search=kw)
        [res_arc.append(x) for x in _res_arc if x not in res_arc]
        ttl_len += len(_res_arc)

    if ttl_len == 0:
        return "没有找到这样的乐曲。"
    elif ttl_len < 80:
        search_result = "为您找到以下结果:\n"
        for res, mid, title, game, symbol in [
            (res_wm, 'id', 'title', '舞萌DX 2022', 'm'),
            (res_uni, 'id', 'title', 'maimai でらっくす UNiVERSE', 'u'),
            (res_chuni, 'id', 'title', 'CHUNITHM NEW!!', 'c'),
            (res_pjsk, 'musicId', 'title', 'Project Sekai', 'p'),
            (res_gbp, 'musicId', 'musicTitle', 'BanG Dream', 'b'),
            (res_ll, 'musicId', 'title', 'Love Live!', 'l'),
            (res_arc, 'musicId', 'title', 'Arcaea', 'a'),
        ]:
            if len(res) == 0:
                continue
            search_result += f"==>{game}"
            search_result += "\n"
            for music in sorted(res, key=lambda i: int(i[mid])):
                if f'\t[{music[mid]}]  {music[title]}' not in search_result:
                    search_result += f"\t[{symbol}{music[mid]}]  {music[title]}\n"
            search_result += "\n"
        r = search_result.strip(
        ) + '\n\n若要查询歌曲详细信息，请发送"/乐曲信息 歌曲id"\n例如"/乐曲信息 m786"'
        ib = BytesIO()
        text_to_image(r).save(ib, format='jpeg')
        return ib.getvalue()

    else:
        return f"结果过多（{ttl_len} 条），请缩小查询范围。"


@Commands("查歌")
async def search_songs(api: BotAPI, message: Message, params: str = None):
    result = search_handler(params, True)
    if isinstance(result, str):
        await message.reply(content=result)
    else:
        await message.reply(file_image=result)
    return True


@Commands("乐曲信息")
async def song_id(api: BotAPI, message: Message, params: str = None):
    if not params:
        await message.reply(content='请在指令后输入乐曲ID')
        return False
    sid = params[1:]
    if not sid.isdigit():
        return
    if params[0] in ['b', 'B']:
        music = bang_dream_total_list.by_id(int(sid))
        if music is not None:
            ib = BytesIO()
            generate_gbp_graph(music).save(ib, 'jpeg', quality=80)
            await message.reply(file_image=ib.getvalue())
            return True
    elif params[0] in ['p', 'P']:
        music = sekai_total_list.by_id(int(sid))
        if music is not None:
            ib = BytesIO()
            generate_sekai_music_graph(music).save(ib, 'jpeg', quality=80)
            await message.reply(file_image=ib.getvalue())
            return True
    elif params[0] in ['m', 'M', 'u', 'U']:
        if params[0] in ['m', 'M']:
            music = maimai_total_list.by_id(sid)
        else:
            music = universe_total_list.by_id(sid)
        if music is not None:
            ib = BytesIO()
            generate_music_graph_new(music, 'music_info').save(ib,
                                                               'jpeg',
                                                               quality=80)
            await message.reply(file_image=ib.getvalue())
            return True
    elif params[0] in ['c', 'C']:
        music = chuni_music_list.by_id(sid)
        if music is not None:
            ib = BytesIO()
            generate_chuni_graph_new(music, 'song_info').save(ib,
                                                              'jpeg',
                                                              quality=80)
            await message.reply(file_image=ib.getvalue())
            return True
    elif params[0] in ['l', 'L']:
        music = ll_total_list.by_id(sid)
        if music is not None:
            result = get_sif_songs(music)
            await message.reply(content=result[0], file_image=result[1])
            return True
    elif params[0] in ['a', 'A']:
        music = arcaea_total_list.by_id(int(sid))
        if music is not None:
            result = get_arcaea_songs(music)
            await message.reply(content=result[0], file_image=result[1])
            return True
    await message.reply(content="没有找到这样的乐曲喔")
    return False