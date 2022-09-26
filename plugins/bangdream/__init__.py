from pathlib import Path
from typing import Optional

from configs.path import IMAGE_PATH, FONT_PATH
from PIL import Image, ImageDraw, ImageFont
from utils.utils import image_to_base64

from .bang_dream_music import *


def generate_gbp_graph(music: GBPMusic) -> Image.Image:
    # Frame
    __band = music.bandName.split('×')[0]
    __band_dict = {
        "ハロー、ハッピーワールド！": 'hhw',
        "Poppin'Party": 'ppp',
        "Afterglow": 'ag',
        "Pastel＊Palettes": 'pp',
        "Roselia": 'roselia',
        "RAISE A SUILEN": 'ras',
        "Morfonica": 'mof',
        "市ヶ谷有咲": 'ppp',
        "Poppin'Party×友希那": 'ppp',
        "Poppin'Party×グリグリ": 'ppp',
        "Roselia×蘭": 'roselia',
        "Poppin'Party×彩×こころ": 'ppp',
        '牛込りみ': 'ppp',
        "戸山香澄": 'ppp',
        "山吹沙綾": 'ppp',
        'ハロハピ×蘭×彩': 'hhw',
        "Afterglow×香澄": 'ag',
        "Pastel＊Palettes×こころ×ましろ": 'pp',
        "RAISE A SUILEN×友希那": 'ras',
        "花園たえ": 'ppp',
        'Afterglow×こころ': 'ag'
    }
    if __band in __band_dict:
        band = __band_dict[__band]
    else:
        band = 'ppp'
    frame = Image.open(IMAGE_PATH / 'bang_dream' / 'assets' /
                       f'Frame_{band}.png').convert('RGBA')
    framew, frameh = frame.size
    base = Image.new('RGBA', (framew, frameh), (0, 0, 0, 0))
    cover = Image.open(IMAGE_PATH / 'bang_dream' / 'jacket' /
                       Path(music.jacket.replace('.webp', '.png'))).resize(
                           (307, 307))
    base.paste(cover, (40, 34))
    base.paste(frame, (0, 0), frame.split()[3])

    # # Title
    titleFontName = FONT_PATH / 'NotoSansSC-Bold.ttf'
    dataDraw = ImageDraw.Draw(base)
    fontsize = 45
    font = ImageFont.truetype(titleFontName.__str__(),
                              fontsize,
                              encoding='utf-8')
    title = music.musicTitle
    if len(title) > 15:
        title = title[0:15] + '...'
    title_w, title_h = font.getsize(title)
    while title_w > 450:
        fontsize -= 2
        font = ImageFont.truetype(titleFontName.__str__(),
                                  fontsize,
                                  encoding='utf-8')
        title_w, title_h = font.getsize(title)
    if band in ['ag', 'hhw', 'mof', 'ppp', 'roselia']:
        dataDraw.text((40, 355), title, 'white', font)
    else:
        dataDraw.text((40, 355), title, 'black', font)

    # Sub title
    font2 = ImageFont.truetype(titleFontName.__str__(), 30, encoding='utf-8')
    pubday = (time.localtime(int(music.publishedAt[:-3])))
    author = f"作词: {music.lyricist[0:18]}..." if len(
        music.lyricist) > 18 else f"作词: {music.lyricist}"
    musician = f"作曲: {music.arranger[0:18]}" if len(
        music.arranger) > 18 else f"作曲: {music.arranger}"
    arranger = f"上线时间: {pubday.tm_year}年{pubday.tm_mon}月"
    date = music.howToGet
    dataDraw.text((40, 438), author, 'black', font2)
    dataDraw.text((40, 478), musician, 'black', font2)
    dataDraw.text((40, 518), arranger, 'black', font2)
    dataDraw.text((40, 558), date, 'black', font2)

    # Difficulty
    level = [str(x) for x in music.difficulty]
    if len(level) == 4:
        level.append('--')
    font3 = ImageFont.truetype(titleFontName.__str__(), 32, encoding='utf-8')

    for diff in range(5):
        levelw, levelh = font3.getsize(level[diff])
        dataDraw.text((450 - levelw / 2, 50 + 63 * diff), level[diff], 'black',
                      font3)
    return base.convert('RGB')


def generate_gbp_reply(music: GBPMusic) -> str:
    title = f'乐曲id: {music.musicId}\n'
    title = f'乐曲名: {music.musicTitle}\n'
    title += f'作词: {music.lyricist}\n'
    title += f'乐队: {music.bandName}\n'
    title += f'作曲: {music.arranger}\n'
    title += f'难度: {str(music.difficulty)[1:-1]}\n'
    pubday = (time.localtime(int(music.publishedAt[:-3])))
    title += f'首次加入于: {pubday.tm_year}年{pubday.tm_mon}月\n'
    title += f'获取方法: {music.howToGet}\n'
    return title


def get_gbp_jacket(music: GBPMusic) -> Optional[str]:
    try:
        jacket_path = music.jacket
        _img = Image.open(IMAGE_PATH / 'bang_dream' / 'jacket' / jacket_path)
        img = str(image_to_base64(_img), encoding='utf-8')
    except Exception as ex:
        print(ex)
        img = None
    return img


def get_bangdream_songs(seed: int = None) -> Tuple:
    music = total_list.random(seed=seed)
    title = generate_gbp_reply(music)
    img = get_gbp_jacket(music)
    return (title, img)