import os

from typing import Optional

from configs.path import FONT_PATH, IMAGE_PATH, DATA_PATH
from PIL import Image, ImageDraw, ImageFont
from .chunithm_music import ChuniMusic, chuniversion, chuni_music_list

level_name = [
    'Basic', 'Advanced', 'Expert', 'Master', 'Ultima', 'World\'s end'
]


def generate_chuni_graph_new(music: ChuniMusic,
                             center_text: Optional[str] = None) -> Image.Image:
    # Frame
    base = Image.open(IMAGE_PATH / 'chunithm' / 'assets' /
                      'chunithm_base.png').convert('RGBA')

    # Cover
    if os.path.exists(IMAGE_PATH / 'chunithm' / 'jackets' / music.jacket):
        cover = Image.open(IMAGE_PATH / 'chunithm' / 'jackets' /
                           music.jacket).resize((744, 744))
    else:
        cover = Image.open(IMAGE_PATH / 'chunithm' / 'assets' /
                           'CHU_UI_Jacket_dummy.png').resize((744, 744))
    base.paste(cover, (39, 230))

    if center_text is not None:
        ctext = Image.open(IMAGE_PATH / 'chunithm' / 'assets' /
                           f'{center_text}.png').convert('RGBA')
        base.paste(ctext, (738, 27), ctext.split()[3])

    # Title
    titleFontName = str(FONT_PATH / 'UDDigiKyokashoN-B.ttc')
    dataDraw = ImageDraw.Draw(base)
    fontsize = 48
    font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
    title = music.title
    title_w, title_h = font.getsize(title)
    while title_w > 900 or title_h > 70:
        fontsize -= 2
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        title_w, title_h = font.getsize(title)
    dataDraw.text((1365 - title_w / 2, 280 - title_h / 2), title, 'black',
                  font)

    # # Sub title
    fontsize = 24
    font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
    author = music.artist
    artist_w, artist_h = font.getsize(author)
    while artist_w > 940 or artist_h > 30:
        fontsize -= 2
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        artist_w, artist_h = font.getsize(title)
    dataDraw.text((1365 - artist_w / 2, 350 - artist_h / 2), author, 'black',
                  font)
    font = ImageFont.truetype(titleFontName, 60, encoding='utf-8')
    if music.bpm is None:
        bpm = 'No BPM Data'
    else:
        bpm = f'{music.bpm} BPM'
    bpm_w, bpm_h = font.getsize(bpm)
    dataDraw.text((1585 - bpm_w / 2, 480 - bpm_h / 2), bpm, 'black', font)

    fontsize = 48
    font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
    genre = music.genre
    genre_w, genre_h = font.getsize(genre)
    while genre_w > 445 or genre_h > 70:
        fontsize -= 2
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        genre_w, genre_h = font.getsize(genre)
    dataDraw.text((1595 - genre_w / 2, 620 - genre_h / 2), genre, 'black',
                  font)
    version_img = Image.open(
        IMAGE_PATH / 'chunithm' / 'assets' /
        f'CHU_Ver_{list(chuniversion.values()).index(music.version)}.png'
    ).convert('RGBA')
    base.paste(version_img, (910, 470), version_img.split()[3])

    # Chart Diff
    diff_pos = [(946, 770), (946, 855), (946, 940), (1485, 770), (1485, 855),
                (1485, 940)]
    charter_pos = [(1180, 780), (1180, 865), (1180, 950), (1720, 780),
                   (1720, 865), (1720, 950)]
    for i in range(6):
        if music.ds[i] != 0:
            if music.ds[i] >= 100:
                ds = music.level[i]
            else:
                ds = '{:.1f}'.format(music.ds[i])
            charter = music.charts[i].charter if music.charts[
                i].charter is not None else '没有譜師信息'
        else:
            ds = '-'
            charter = f'没有{level_name[i]}的譜面'

        fontsize = 40
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        diff_w, diff_h = font.getsize(ds)
        dataDraw.text(
            (diff_pos[i][0] - diff_w / 2, diff_pos[i][1] - diff_h / 2), ds,
            'black', font)
        charter_w, charter_h = font.getsize(charter)
        while charter_w > 325 or charter_h > 35:
            fontsize -= 2
            font = ImageFont.truetype(titleFontName,
                                      fontsize,
                                      encoding='utf-8')
            charter_w, charter_h = font.getsize(charter)
        dataDraw.text((charter_pos[i][0] - charter_w / 2,
                       charter_pos[i][1] - charter_h / 2), charter, 'black',
                      font)
    return base.convert('RGB')