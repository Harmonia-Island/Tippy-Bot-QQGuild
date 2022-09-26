import os
import math
from typing import Union

from configs.path import FONT_PATH, IMAGE_PATH
from PIL import Image, ImageDraw, ImageFont

from .maimaidx_music import MaiMusic

level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:Master']


def computeRa(ds: float, achievement: float, spp: bool = False) -> int:
    baseRa = 22.4 if spp else 14.0
    if achievement < 50:
        baseRa = 0.0 if spp else 0.0
    elif achievement < 60:
        baseRa = 8.0 if spp else 5.0
    elif achievement < 70:
        baseRa = 9.6 if spp else 6.0
    elif achievement < 75:
        baseRa = 11.2 if spp else 7.0
    elif achievement < 80:
        baseRa = 12.0 if spp else 7.5
    elif achievement < 90:
        baseRa = 13.6 if spp else 8.5
    elif achievement < 94:
        baseRa = 15.2 if spp else 9.5
    elif achievement < 97:
        baseRa = 16.8 if spp else 10.5
    elif achievement < 98:
        baseRa = 20.0 if spp else 12.5
    elif achievement < 99:
        baseRa = 20.0 if spp else 12.7
    elif achievement < 99.5:
        baseRa = 20.8 if spp else 13.0
    elif achievement < 100:
        baseRa = 21.1 if spp else 13.2
    elif achievement < 100.5:
        baseRa = 21.6 if spp else 13.5
    return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)


def _resizePic(img: Image.Image, time: float):
    return img.resize((int(img.size[0] * time), int(img.size[1] * time)))


def draw_level(level: str, level_str: str) -> Image.Image:
    # Difficulty
    img = Image.new('RGBA', (192, 60), (0, 0, 0, 0))
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
    else:
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

    _lv = diff_font.crop(
        (int(img_x[2]), int(img_y[3]), int(img_x[2] + (df_x / 4)),
         int(img_y[3] + (df_y / 4))))
    img.paste(_lv, (0, 0), _lv.split()[3])
    for turn in range(len(diff_start_pos)):
        pos = diff_start_pos[turn]
        _temp = diff_font.crop(
            (int(pos[0]), int(pos[1]), int(pos[0] + (df_x / 4)),
             int(pos[1] + (df_y / 4))))
        if len(level.replace('+', '')) == 1:
            img.paste(_temp, (40 + int(30 * turn), 0), _temp.split()[3])
        else:
            img.paste(_temp, (35 + int(30 * turn), 0), _temp.split()[3])
    return img


def draw_achievement(achievement: Union[int, float]) -> Image.Image:
    # Difficulty
    # font = ImageFont.truetype(titleFontName, 70, encoding='utf-8')
    img = Image.new('RGBA', (720, 118), (0, 0, 0, 0))

    if achievement >= 97:
        ach_base = 'UI_Num_Score_1110000_Gold.png'
        per_base = 'UI_RSL_Score_Per_Gold.png'
    elif achievement >= 80:
        ach_base = 'UI_Num_Score_1110000_Red.png'
        per_base = 'UI_RSL_Score_Per_Red.png'
    else:
        ach_base = 'UI_Num_Score_1110000_Blue.png'
        per_base = 'UI_RSL_Score_Per_Blue.png'

    ach_font = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                          ach_base).convert('RGBA')
    df_x, df_y = ach_font.size
    img_x = [int(x) for x in range(df_x) if (x % (df_x / 4) == 0)]
    img_y = [int(y) for y in range(df_y) if (y % (df_y / 4) == 0)]

    diff_start_pos = []
    if int(achievement) == achievement:
        s_ach = f'{int(achievement)}.0000'
    else:
        s_ach = str(achievement).split('.')[0] + ".{:0<4}".format(
            str(achievement).split('.')[-1])

    for _diff in s_ach:
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
        elif _diff in ['1', '5', '9', '.']:
            a_x = img_x[1]
        elif _diff in ['2', '6', '+']:
            a_x = img_x[2]
        else:
            a_x = img_x[3]
        if _diff == '.':
            diff_start_pos.append(None)
        diff_start_pos.append((a_x, a_y))

    turn = 0
    offset = 0
    for pos in diff_start_pos:
        if pos is None:
            offset = -20
            continue
        if diff_start_pos[turn - 1] is None:
            offset = -40
        _temp = ach_font.crop(
            (int(pos[0]), int(pos[1]), int(pos[0] + (df_x / 4)),
             int(pos[1] + (df_y / 4))))
        if diff_start_pos[turn] is None:
            img.paste(_temp, (int((df_x / 4) * turn) + offset, 18),
                      _temp.split()[3])
        else:
            img.paste(_temp, (int((df_x / 4) * turn) + offset, 0),
                      _temp.split()[3])
        turn += 1
    percentage = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                            per_base).convert('RGBA')
    img.paste(percentage, (int((df_x / 4) * turn) + offset - 5, 40),
              percentage.split()[3])
    return img


def generate_recom_frame(music: MaiMusic, achievements: Union[list, tuple],
                         level_index: int) -> Image.Image:
    diff_i = ['BSC', 'ADV', 'EXP', 'MST', 'MST_Re']
    img = Image.open(
        IMAGE_PATH / 'maimai' / 'assets' /
        f'UI_CMN_RSL_KopMBase_{diff_i[level_index]}.png').convert('RGBA')
    # Difficulties
    diff = draw_level(music.level[level_index], level_name[level_index])
    diff = _resizePic(diff, 0.65)
    img.paste(diff, (545, 40), diff.split()[3])
    # Title
    titleFontName = str(FONT_PATH / 'adobe_simhei.otf')
    dataDraw = ImageDraw.Draw(img)
    titleFont = ImageFont.truetype(titleFontName, 13, encoding='utf-8')
    title = music.title
    dataDraw.text((330, 15), title, 'white', titleFont)
    # Rating
    rating_old = computeRa(ds=music.ds[level_index],
                           achievement=achievements[0],
                           spp=False)
    rating_new = computeRa(ds=music.ds[level_index],
                           achievement=achievements[1],
                           spp=False)
    ratingFont = ImageFont.truetype(titleFontName, 18, encoding='utf-8')
    dataDraw.text((545, 113), f'{rating_old} > {rating_new}', '#2047a8',
                  ratingFont)
    # Info
    infoFont = ImageFont.truetype(str(FONT_PATH / 'msyhbd.ttc'),
                                  15,
                                  encoding='utf-8')
    charter = music.charts[level_index]['charter']
    if len(charter) > 10:
        charter = charter[:9]
    info = f"定数: {music.ds[level_index]}    谱师: {charter}    BPM: {music.bpm}"
    dataDraw.text((140, 110), info, 'black', infoFont)
    # Achievement
    ach_old = draw_achievement(achievements[0])
    ach_old = _resizePic(ach_old, 0.2)
    img.paste(ach_old, (145, 65), ach_old.split()[3])
    arrow = Image.open(
        IMAGE_PATH / 'maimai' / 'assets' /
        'UI_STG_Photo_Preview_CameraArrow.png').convert('RGBA').resize(
            (43, 50))
    if achievements[0] > 100:
        arrow_pos = (290, 50)
    else:
        arrow_pos = (280, 50)
    img.paste(arrow, arrow_pos, arrow.split()[3])
    ach_new = draw_achievement(achievements[1])
    ach_new = _resizePic(ach_new, 0.29)
    img.paste(ach_new, (330, 60), ach_new.split()[3])
    # Cover
    coverPath = IMAGE_PATH / 'maimai' / 'cover' / f'{music.id}.png'
    if not os.path.exists(coverPath):
        coverPath = IMAGE_PATH / 'maimai' / 'cover' / 'default.png'
    cover = Image.open(coverPath).convert('RGB').resize((117, 117))
    img.paste(cover, (12, 12))
    # Type
    if music.type == 'DX':
        _type = Image.open(
            IMAGE_PATH / 'maimai' / 'assets' /
            'UI_UPE_Infoicon_DeluxeMode.png').convert('RGBA').resize((84, 23))
    else:
        _type = Image.open(
            IMAGE_PATH / 'maimai' / 'assets' /
            'UI_UPE_Infoicon_StandardMode.png').convert('RGBA').resize(
                (84, 23))
    img.paste(_type, (548, 84), _type.split()[3])

    return img