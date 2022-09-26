import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Union

import aiohttp
from configs.path import IMAGE_PATH, FONT_PATH
from configs.config import config
from PIL import Image, ImageDraw, ImageFont


def get_local_proxy():
    """
    说明：
        获取 config.py 中设置的代理
    """
    if sys.platform == "darwin":
        return config['proxy_mac']
    return config['proxy_win']


async def download_image(url: str,
                         save_path: Union[Path, str],
                         use_proxy: bool = False) -> None:
    """
    说明：
        快捷下载图片
    参数：
        :param url: 图片链接
    """
    proxy = get_local_proxy() if use_proxy else None
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10, proxy=proxy) as response:
            data = await response.read()
    img = Image.open(BytesIO(data)).convert('RGB').save(save_path,
                                                        "jpeg",
                                                        quality=80)
    return None


async def user_avatar_rounded(qq: Union[int, str], user_id=None) -> bytes:
    """
    说明：
        快捷获取用户头像
    参数：
        :param qq: qq号
    """
    if user_id is None:
        user_id = qq
    if not os.path.exists(IMAGE_PATH / 'user_avatar'):
        os.mkdir(IMAGE_PATH / 'user_avatar')
    elif os.path.exists(IMAGE_PATH / 'user_avatar' / f'{user_id}.png') and (
            time.time() - os.path.getmtime(
                IMAGE_PATH / 'user_avatar' / f'{user_id}.png') < 604800):
        return 'OK'
    if 'http' in qq:
        url = qq
    else:
        url = f"http://q1.qlogo.cn/g?b=qq&nk={qq}&s=100"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=5) as response:
            data = await response.read()

    img = Image.open(BytesIO(data))

    circle_corner(img, 10, IMAGE_PATH / 'user_avatar' / f'{user_id}.png')
    return 'OK'


def graphical_text_msg(word: str) -> list:
    """
    说明：
        将字符串消息转为图片
    参数：
        :param word: 文本
    """
    return [{
        "type": "image",
        "data": {
            "file":
            f"base64://{str(image_to_base64(text_to_image(word)), encoding='utf-8')}"
        }
    }]


def circle_corner(img, radii, filename=0):
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建黑色方形
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形
    img = img.convert("RGBA")
    w, h = img.size

    alpha = Image.new('L', img.size, 255)  # 与img同大小的白色矩形，L 表示黑白图
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                (0, h - radii))  # 左下角

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    if filename:
        img.save(f'{filename}', 'PNG', qulity=100)
        return 'OK'
    else:
        return img


def image_to_base64(img, format='PNG'):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


def text_to_image(in_text):
    fontpath = str(FONT_PATH / 'msyh.ttc')
    font = ImageFont.truetype(fontpath, 24)
    padding = 10
    margin = 4
    text = shorten_text(in_text)
    text_list = text.split('\n')
    max_width = 0
    for text in text_list:
        w, h = font.getsize(text)
        max_width = max(max_width, w)
    wa = max_width + padding * 2
    ha = h * len(text_list) + margin * (len(text_list) - 1) + padding * 2
    i = Image.new('RGB', (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(i)
    for j in range(len(text_list)):
        text = text_list[j]
        draw.text((padding, padding + j * (margin + h)),
                  text,
                  font=font,
                  fill=(0, 0, 0))
    return i


def shorten_text(text):
    mark = 0
    new = ''
    for i in range(len(text)):
        mark += 1
        if text[i] == '\n':
            mark = 0
        if mark > 50:
            new = new + '\n' + text[i]
            mark = 0
        else:
            new += text[i]
    return new
