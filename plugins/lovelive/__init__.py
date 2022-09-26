from io import BytesIO

from configs.path import IMAGE_PATH
from PIL import Image

from .lovelivemusic import *


def get_sif_songs(music: LoveLiveMusic, seed=None):

    # title = f'乐曲id: {_ar["musicId"]}\n'
    title = f'ID: {music.musicId}\n'\
            + f'乐曲名: {music.title}\n'\
            + f'演唱: {music.member_tag}\n'\
            + f'时长: {music.live_time}\n'

    # try:
    _img = Image.open(IMAGE_PATH / 'lovelive' / 'jacket' /
                      music.jacket).convert('RGB')
    img = BytesIO()
    _img.save(img, format='jpeg')
    return (title, img.getvalue())
