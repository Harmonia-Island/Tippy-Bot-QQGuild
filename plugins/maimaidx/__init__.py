from io import BytesIO
import time

import aiohttp
import os
from botpy import BotAPI
from PIL import Image, ImageDraw, ImageFont
from botpy.ext.command_util import Commands
from botpy.message import Message
from models.maimaidx import MaimaiUserData
from service.log import logger
from utils.utils import user_avatar_rounded

from .maimai_best_40 import get_user_info, generate
from .maimaidx_music import MaiMusic, maimai_versions, total_list_jp, total_list
from typing import Optional
from configs.path import IMAGE_PATH, FONT_PATH


def _resizePic(img: Image.Image, time: float):
    return img.resize((int(img.size[0] * time), int(img.size[1] * time)))


def generate_music_graph_new(music: MaiMusic,
                             center_text: Optional[str] = None) -> Image.Image:
    # Frame
    frame = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                       'Song_Frame.png').convert('RGBA')
    framew, frameh = frame.size
    base = Image.new('RGBA', (framew, frameh), (0, 0, 0, 0))

    # Cover
    if os.path.exists(IMAGE_PATH / 'maimai' / 'cover' / f'{music.id}.png'):
        cover = Image.open(IMAGE_PATH / 'maimai' / 'cover' /
                           f'{music.id}.png').resize((570, 570))
    elif os.path.exists(IMAGE_PATH / 'maimai' / 'cover' / f'{music.id}.jpg'):
        cover = Image.open(IMAGE_PATH / 'maimai' / 'cover' /
                           f'{music.id}.jpg').resize((570, 570))
    else:
        cover = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                           'UI_MSS_MusicLock_MST.png').resize((570, 570))
    base.paste(cover, (478, 120))
    base.paste(frame, (0, 0), frame.split()[3])

    if center_text is not None:
        ctext = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                           f'{center_text}.png').convert('RGBA')
        __cw, __ch = ctext.size
        base.paste(ctext, (int(550 - __cw / 2), 2), ctext.split()[3])

    # # Map type
    if music.type == 'DX':
        mapType = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                             'music_dx.png').convert('RGBA').resize((71, 20))
    else:
        mapType = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                             'music_standard.png').convert('RGBA').resize(
                                 (71, 20))
    base.paste(mapType, (408, 385), mapType.split()[3])

    # Title
    titleFontName = str(FONT_PATH / 'UDDigiKyokashoN-B.ttc')
    dataDraw = ImageDraw.Draw(base)
    fontsize = 36
    font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
    title = music.title
    title_w, title_h = font.getsize(title)
    while title_w > 428 or title_h > 50:
        fontsize -= 1
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        title_w, title_h = font.getsize(title)
    dataDraw.text((320 - title_w / 2, 171 - title_h / 2), title, 'white', font)

    # author
    fontsize = 24
    author = music.artist
    font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
    author_w, author_h = font.getsize(author)
    while author_w > 300 or author_h > 30:
        fontsize -= 1
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        author_w, author_h = font.getsize(author)
    dataDraw.text((315 - author_w / 2, 247 - author_h / 2), author, 'black',
                  font)

    font = ImageFont.truetype(titleFontName, 22, encoding='utf-8')
    dataDraw.text((517, 287), f"{music.bpm}", 'white', font)
    font = ImageFont.truetype(titleFontName, 18, encoding='utf-8')
    if 'CN' in maimai_versions[music.version] or int(music.id) < 1000:
        mid = f"m{music.id}"
    else:
        mid = f"u{music.id}"
    dataDraw.text((227, 289), f"{mid}", 'white', font)
    genre_d = {
        'niconicoボーカロイド': 'Niconico',
        '東方Project': 'Toho',
        'ゲームバラエティ': 'Variety',
        'オンゲキCHUNITHM': 'Chugeki',
        'maimai': 'Original',
        'POPSアニメ': 'PopsAnime'
    }
    mapGenre = Image.open(
        IMAGE_PATH / 'maimai' / 'assets' /
        f'UI_CMN_TabTitle_{genre_d[music.genre]}.png').convert('RGBA')
    base.paste(mapGenre, (356, 316), mapGenre.split()[3])

    if len(str(music.id)) == 5:
        if str(music.id)[:2] == '10':
            j_id = str(int(str(music.id)[2:]))
        else:
            j_id = str(music.id)[1:]
    else:
        j_id = str(music.id)

    if 'CN' in maimai_versions[music.version]:
        maiLogoCN = Image.open(
            IMAGE_PATH / 'maimai' / 'assets' /
            f'UI_CMN_TabTitle_MaimaiTitle_Ver{maimai_versions[music.version]}.png'
        ).convert('RGBA').resize((186, 89))
        base.paste(maiLogoCN, (75, 313), maiLogoCN.split()[3])
    else:
        jp_music = total_list_jp.by_id(j_id)
        if jp_music is not None:
            jp_version = jp_music.version
            maiLogo = Image.open(
                IMAGE_PATH / 'maimai' / 'assets' /
                f'UI_CMN_TabTitle_MaimaiTitle_Ver{maimai_versions[jp_version]}.png'
            ).convert('RGBA').resize((186, 89))
            base.paste(maiLogo, (75, 313), maiLogo.split()[3])

    # # Difficulty
    for maidiff in range(5):
        if len(music.ds) != 5:
            music.level.append('--')
            music.ds.append(' --')
            music.charts.append({"charter": None, "notes": []})
        level = music.level[maidiff]
        ds_s = music.ds[maidiff]
        level_str = ['Basic', 'Advanced', 'Expert', 'Master',
                     'ReMaster'][maidiff]
        mapper = music.charts[maidiff]['charter'] if music.charts[maidiff][
            'charter'] is not None else '-'
        diff_f = ' '.join(level).split()

        # Style
        if level_str == 'Basic':
            diff_index = '01'
        elif level_str == 'Advanced':
            diff_index = '02'
        elif level_str == 'Expert':
            diff_index = '03'
        elif level_str == 'Master':
            diff_index = '04'
        elif level_str == 'ReMaster':
            diff_index = '05'

        diff_font_file = f'UI_NUM_MLevel_{diff_index}.png'
        diff_font = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                               diff_font_file).convert('RGBA')
        df_x, df_y = diff_font.size
        img_x = [int(x) for x in range(df_x) if (x % (df_x / 4) == 0)]
        img_y = [int(y) for y in range(df_y) if (y % (df_y / 4) == 0)]

        diff_start_pos = []

        for _diff in diff_f:
            if _diff in ['0', '1', '2', '3']:
                a_y = img_y[0]
            elif _diff in ['4', '5', '6', '7']:
                a_y = img_y[1]
            elif _diff in ['8', '9', '+', '-']:
                a_y = img_y[2]
            else:
                a_y = img_y[3]
            if _diff in ['0', '4', '8']:
                a_x = img_x[0]
            elif _diff in ['1', '5', '9']:
                a_x = img_x[1]
            elif _diff in ['2', '6', '+']:
                a_x = img_x[2]
            else:
                a_x = img_x[3]
            diff_start_pos.append((a_x, a_y))

        for turn in range(len(diff_start_pos)):
            pos = diff_start_pos[turn]
            _temp = diff_font.crop(
                (int(pos[0]), int(pos[1]), int(pos[0] + (df_x / 4)),
                 int(pos[1] + (df_y / 4))))
            _temp = _resizePic(_temp, 0.8)
            if len(level.replace('+', '')) == 1:
                base.paste(_temp, (65 + int(25 * turn), (440 + 50 * maidiff)),
                           _temp.split()[3])
            else:
                if diff_f[turn] == '+':
                    base.paste(_temp,
                               (55 + int(27 * turn), (440 + 50 * maidiff)),
                               _temp.split()[3])
                else:
                    base.paste(_temp,
                               (62 + int(23 * turn), (440 + 50 * maidiff)),
                               _temp.split()[3])
                # print(f'pasted + {(460 + int(50*turn), 685)}')
            font = ImageFont.truetype(titleFontName, 25, encoding='utf-8')
            ds_w, ds_h = font.getsize(str(ds_s))
            dataDraw.text((180 - ds_w / 2, (452 + 50 * maidiff)), str(ds_s),
                          'black', font)
            dataDraw.text((261, (452 + 50 * maidiff)), mapper, 'black', font)

    # base.show()
    return base.convert('RGB')


# 舞萌排名
@Commands("舞萌排名")
async def mairank(api: BotAPI, message: Message, params: str = None):
    # 第一种用reply发送消息
    # logger.info(params)
    user_info = await MaimaiUserData.get_info(guild_id=message.author.id)
    if user_info is None:
        await message.reply(content='您还没有绑定查分器账号！请先绑定账号再试')
        return False
    user_id = user_info.username
    async with aiohttp.request(
            "GET",
            "https://www.diving-fish.com/api/maimaidxprober/rating_ranking"
    ) as resp:
        rank_data = await resp.json()
        sorted_rank_data = sorted(rank_data,
                                  key=lambda r: r['ra'],
                                  reverse=True)
        ttl_num = len(sorted_rank_data)
        if user_id in [r['username'].lower() for r in sorted_rank_data]:
            rank_index = [r['username'].lower()
                          for r in sorted_rank_data].index(user_id) + 1
            # nickname = sorted_rank_data[rank_index - 1]['username']
            await message.reply(
                content=
                f'截止至 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n\n您的DX Rating在所有注册查分器的用户中排行第{rank_index}/共{ttl_num}'
            )
            return True
        else:
            await message.reply(content='未找到该玩家')
            return False


# best 40
@Commands("舞萌b40")
async def maib40(api: BotAPI, message: Message, params: str = None):
    username = params
    isHost = False
    if username == "":
        user_info = await MaimaiUserData.get_info(guild_id=message.author.id)
        if user_info is None:
            await message.reply(content='您还没有绑定查分器账号！请先绑定账号再试')
            return False
        user_name = user_info.username
        await user_avatar_rounded(message.author.avatar, message.author.id)
        payload = {'username': user_name}
        isHost = True
    elif username in ['理论值', 'maxrating', 'MaxRating']:
        payload = {'username': "maxscore"}
    else:
        payload = {'username': username}

    b50 = False
    if b50:
        payload['b50'] = True
    img, success = await generate(payload, message.author, isHost, False)
    if success == 400:
        await message.reply(content="未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
        return False
    elif success == 403:
        await message.reply(content='该用户禁止了其他人获取数据。')
        return False
    else:
        ib = BytesIO()
        img.save(ib, 'jpeg', quality=90)
        await message.reply(file_image=ib.getvalue())
        return True