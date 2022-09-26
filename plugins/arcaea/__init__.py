import time
from io import BytesIO
from configs.path import IMAGE_PATH
from PIL import Image

from .arcaea_music import *


def get_arcaea_songs(music: ArcaeaMusic, seed=None):

    # title = f'乐曲id: {_ar["musicId"]}\n'
    title = f'id: {music.musicId}\n'
    title += f'乐曲名: {music.title}\n'
    title += f'作曲: {music.artist}\n'
    title += f'BPM: {music.bpm}\n'
    title += f'曲包: {music.package}\n'
    title += f'上线版本: Arcaea {music.version}\n'
    title += f'上线时间: {time.strftime("%Y-%m-%d", time.localtime(music.date))}\n'
    title += f'难度: {"/".join([str(x) for x in music.difficulty])}\n'

    # try:
    _img = Image.open(IMAGE_PATH / 'arcaea' / 'cover' /
                      f'{music.songId}.jpg').convert('RGB')
    img = BytesIO()
    _img.save(img, format='jpeg')
    return (title, img.getvalue())