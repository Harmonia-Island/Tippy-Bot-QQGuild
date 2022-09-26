from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from configs.path import IMAGE_PATH, FONT_PATH
from utils.utils import image_to_base64

from .pjsk_music import *


def generate_sekai_reply(music: SekaiMusic) -> str:
    title = f'乐曲id: {music.musicId}\n'
    title += f'乐曲名: {music.title}\n'
    title += f'作词: {music.lyricist}\n'
    title += f'编曲: {music.arranger}\n'
    title += f'作曲: {music.composer}\n'
    title += f'Vocal: {", ".join(music.vocals)}\n'
    title += f'难度: {", ".join([str(x) for x in music.difficulty])}\n\n'
    return title


def get_sekai_jacket(music: SekaiMusic) -> Optional[str]:
    try:
        _img = Image.open(IMAGE_PATH / 'pjsk' / 'jacket' /
                          f'{music.musicId}.png')
        img = str(image_to_base64(_img), encoding='utf-8')
    except Exception:
        img = None
    return img


def generate_sekai_music_graph(music: SekaiMusic) -> Image.Image:
    # Frame
    frame = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                       'Song_Frame.png').convert('RGBA')
    framew, frameh = frame.size
    base = Image.new('RGBA', (framew, frameh), (0, 0, 0, 0))
    cover = Image.open(IMAGE_PATH / 'pjsk' / 'jacket' /
                       f'{music.musicId}.png').resize((388, 388))
    base.paste(cover, (27, 27))
    base.paste(frame, (0, 0), frame.split()[3])

    # # Title
    titleFontName = FONT_PATH / 'adobe_simhei.otf'
    dataDraw = ImageDraw.Draw(base)
    fontsize = 45
    font = ImageFont.truetype(titleFontName.__str__(),
                              fontsize,
                              encoding='utf-8')
    title = music.title
    if len(title) > 18:
        title = title[0:18] + '...'
    title_w, title_h = font.getsize(title)
    while title_w > 480 or title_h > 70:
        fontsize -= 2
        font = ImageFont.truetype(titleFontName.__str__(),
                                  fontsize,
                                  encoding='utf-8')
        title_w, title_h = font.getsize(title)
    dataDraw.text((790 - title_w / 2, 55), title, 'white', font)

    # Sub title
    font2 = ImageFont.truetype(titleFontName.__str__(), 30, encoding='utf-8')
    author = music.lyricist
    musician = music.composer
    arranger = music.arranger
    dataDraw.text((560, 260), author, 'white', font2)
    dataDraw.text((560, 312.5), musician, 'white', font2)
    dataDraw.text((560, 367.5), arranger, 'white', font2)

    # MV
    mv_type = music.categories
    mt_layer = 0
    if 'mv_2d' in mv_type:
        mv = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                        '2dmv.png').convert('RGBA')
        base.paste(mv, (1000, 350), mv.split()[3])
        mt_layer += 1
    if 'mv_3d' in mv_type or 'mv' in mv_type:
        mv = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                        '3dmv.png').convert('RGBA')
        base.paste(mv, (1000 - 75 * mt_layer, 350), mv.split()[3])
        mt_layer += 1
    if 'original' in mv_type:
        mv = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                        'origmv.png').convert('RGBA')
        base.paste(mv, (1000 - 75 * mt_layer, 350), mv.split()[3])
        mt_layer += 1
    if mt_layer == 0:
        mv = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                        'nomv.png').convert('RGBA')
        base.paste(mv, (1000, 350), mv.split()[3])

    # Difficulty
    level = [str(x) for x in music.difficulty]
    font3 = ImageFont.truetype(titleFontName.__str__(), 36, encoding='utf-8')

    for diff in range(5):
        dataDraw.text(((518 + 125.025 * diff), 177), level[diff], 'white',
                      font3)

    # Icon
    vsinger_ver = []
    for __tmp in music.characters:
        if __tmp[
                0] == "\u30d0\u30fc\u30c1\u30e3\u30eb\u30fb\u30b7\u30f3\u30ac\u30fcver.":
            for c in __tmp[1]:
                vsinger_ver.append(str(c['characterId']))
    sekai_ver = []
    for __tmp in music.characters:
        if __tmp[0] == "\u30bb\u30ab\u30a4ver.":
            for c in __tmp[1]:
                sekai_ver.append(str(c['characterId']))
    inst_ver = ("Inst.ver." in music.vocals)
    if inst_ver:
        __inst = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                            'instonly.png').convert('RGBA')
        base.paste(__inst, (0, 430), __inst.split()[3])

    # sekai ver
    if not inst_ver:
        if len(sekai_ver) != 0:
            for _s in sekai_ver:
                __temp = Image.open(IMAGE_PATH / 'pjsk' / 'assets' / 'chr_ts' /
                                    f'chr_ts_{_s}.png').convert('RGBA').resize(
                                        (77, 77))
                base.paste(__temp, (17 + 95 * sekai_ver.index(_s), 482),
                           __temp.split()[3])
        else:
            __temp = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                                'vsingeronly.png').convert('RGBA')
            base.paste(__temp, (0, 476), __temp.split()[3])
        # vsinger ver
        if len(vsinger_ver) != 0:
            for _v in vsinger_ver:
                __temp = Image.open(IMAGE_PATH / 'pjsk' / 'assets' / 'chr_ts' /
                                    f'chr_ts_{_v}.png').convert('RGBA').resize(
                                        (77, 77))
                base.paste(__temp, (600 + 95 * vsinger_ver.index(_v), 482),
                           __temp.split()[3])
        else:
            __temp = Image.open(IMAGE_PATH / 'pjsk' / 'assets' /
                                'sekaionly.png').convert('RGBA')
            base.paste(__temp, (590, 476), __temp.split()[3])
    return base.convert('RGB')


def get_pjsk_songs(seed=None):
    music = total_list.random(seed)
    title = generate_sekai_reply(music)
    img = get_sekai_jacket(music)
    return (title, img)