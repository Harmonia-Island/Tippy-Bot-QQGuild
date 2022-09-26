from botpy import BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message
from io import BytesIO
import json
import os
import random
import time
from typing import Optional

from configs.path import FONT_PATH, TXT_PATH, IMAGE_PATH
from PIL import Image, ImageDraw, ImageFont
from utils.utils import user_avatar_rounded, download_image

from plugins.bangdream import generate_gbp_graph, total_list as gbp_total_list
from plugins.maimaidx import generate_music_graph_new, total_list as maimai_list
from plugins.chunithm import generate_chuni_graph_new, chuni_music_list
from plugins.pjsk import generate_sekai_music_graph, total_list as pjsk_list
from plugins.vtuber import get_vtubers

ongame_dict = json.load(open(TXT_PATH / 'onngame.json', 'r', encoding="utf8"))
vtubers = json.load(open(TXT_PATH / 'vtbs.json', 'r', encoding="utf8"))

ys_ls = [
    '拼机', ('推分', '越级', '下埋'), '夜勤', ('练底力', '练手法'), '打旧框',
    '干饭', ('抓绝赞', '收歌'), '看live', '学习', '厄介', ('调戏bot', '调戏群主'),
    ('刷微博', '刷知乎', '刷b站'), '交肾', ('刷贴吧',
                                  '刷nga'), '拼游戏币', '扩列', ('梭哈', '买入', '卖出'),
    ('看A手', '看holo', '看彩虹'), '挂人', '背单词', '做奥术', 'aeg', 'MC', 'Apex', '撸代码',
    'EH', '听歌', '声讨叔叔', '纯k', '约饭', '看生放', '看瑟图', '看油管', '补番', '斗地主', '挖坑',
    '雀魂', '撸铁', '看管', '看🐒', '减肥', '刷AP', '原神', '抓滴蜡熊', '玩滴蜡熊', '发色图', '约会',
    ('催更华立', '催SEGA'), '打自制', '打adx', '网易云', '郊游', '大吃特吃', '摸摸提比', '摸摸铃酱',
    '开坦克', ('KFC', 'M记'), '发呆', '冥想'
]


def get_maimai_img(seed: Optional[str]) -> Image.Image:
    # maimai_str = "\n千雪&提比提醒您: 打机时不要大力拍打或滑动哦\n\n今日推荐舞萌乐曲：\n"
    music = maimai_list.random(seed)
    return generate_music_graph_new(music, "recommend_today")


def generate_jrys_graph(seed: str,
                        user_info: dict,
                        vtuber_info: Optional[dict],
                        frame_id: Optional[str] = None):
    _wm_key = random.choice(list(ongame_dict.keys()))
    ongame = (random.choice(ongame_dict[_wm_key]))
    _ys_ls_tmp = ys_ls[:]

    # Frame
    if frame_id is None:
        frame_id = '200101'
    frame = Image.open(IMAGE_PATH / 'maimai' / 'mapassets' /
                       'UI_Frame_{:0>6}.png'.format(frame_id)).convert('RGBA')
    framew, frameh = frame.size
    base = Image.new('RGBA', (framew, frameh), (0, 0, 0, 0))
    base.paste(frame, (0, 0), frame.split()[3])

    # Avatar
    avatar = Image.open(IMAGE_PATH / 'user_avatar' /
                        f'{user_info["user_id"]}.png').convert('RGBA').resize(
                            (97, 97))
    base.paste(avatar, (16, 16), avatar.split()[3])
    avatar_frame = Image.open(IMAGE_PATH / 'jrys' / 'assets' /
                              'Bar_Frame.png').convert('RGBA')
    base.paste(avatar_frame, (13, 13), avatar_frame.split()[3])

    # Username
    titleFontName = FONT_PATH / 'NotoSansSC-Bold.ttf'
    dataDraw = ImageDraw.Draw(base)
    fontsize = 32
    font = ImageFont.truetype(titleFontName.__str__(),
                              fontsize,
                              encoding='utf-8')
    title = user_info['nickname']
    if len(title) > 15:
        title = title[0:15] + '...'
    dataDraw.text((125, 25), title, 'black', font)

    # Sub title
    font2 = ImageFont.truetype(titleFontName.__str__(), 18, encoding='utf-8')
    daytime = 60
    pubday = time.localtime(time.time())
    wday = ['一', '二', '三', '四', '五', '六', '日']
    dateT = f"{pubday.tm_year}年{pubday.tm_mon}月{pubday.tm_mday}日  星期{wday[pubday.tm_wday]}"
    dataDraw.text((125, 75), dateT, 'black', font2)

    # Main Frame
    main_frame = Image.open(IMAGE_PATH / 'jrys' / 'assets' /
                            'Dialog_Frame.png').convert('RGBA')
    base.paste(main_frame, (5, 115), main_frame.split()[3])

    # Text
    _t = time.strftime("%Y-%m-%d", time.localtime())
    _h = int(time.strftime("%H", time.localtime()))
    seed = f'{_t}-{user_info["nickname"]}'
    if _h in [12, 13]:
        _hs = '中午'
    elif _h < 12 and _h > 5:
        _hs = '早上'
    elif _h < 18 and _h > 12:
        _hs = '下午'
    else:
        _hs = '晚上'
    font2 = ImageFont.truetype(titleFontName.__str__(), 20, encoding='utf-8')
    ys_txt = f"{_hs}好！\n推荐游戏平台: {_wm_key}\n推荐音游: {ongame[0:10] if len(ongame) > 10 else ongame}\n街机黄金位: "
    dataDraw.text((30, 160), ys_txt, 'black', font2)

    # Arcade pos
    pos = random.choice(["1P", "2P"])
    arcade_pos = Image.open(IMAGE_PATH / 'jrys' / 'assets' /
                            f'UI_CDR_{pos}.png').convert('RGBA').resize(
                                (37, 29))
    base.paste(arcade_pos, (140, 238), arcade_pos.split()[3])

    # Lucky point
    luckypoint = random.randint(0, 101)
    if luckypoint > 50:
        lucky_life = '01'
    elif luckypoint > 30:
        lucky_life = '02'
    elif luckypoint > 10:
        lucky_life = '03'
    else:
        lucky_life = '04'
    luckypoint_frame = Image.open(
        IMAGE_PATH / 'jrys' / 'assets' /
        f'UI_DNM_Base_Life_{lucky_life}.png').convert('RGBA').resize((90, 90))

    diff_font_file = f'UI_DNM_LifeNum_{lucky_life}.png'
    diff_font = Image.open(IMAGE_PATH / 'jrys' / 'assets' /
                           diff_font_file).convert('RGBA')
    df_x, df_y = diff_font.size
    img_x = [int(x) for x in range(df_x) if (x % (df_x / 4) == 0)]
    img_y = [int(y) for y in range(df_y) if (y % (df_y / 4) == 0)]
    diff_start_pos = []

    for _diff in str(luckypoint):
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
    __temp_base = Image.new('RGBA', (24 * len(str(luckypoint)), 30),
                            (0, 0, 0, 0))
    for turn in range(len(diff_start_pos)):
        pos = diff_start_pos[turn]
        _temp = diff_font.crop(
            (int(pos[0]), int(pos[1]), int(pos[0] + (df_x / 4)),
             int(pos[1] + (df_y / 4)))).resize((26, 30))
        __temp_base.paste(_temp, (24 * turn, 0), _temp.split()[3])
    __t_w, __t_h = __temp_base.size
    __l_w, __l_h = luckypoint_frame.size
    luckypoint_frame.paste(__temp_base, (int(
        (__l_w - __t_w) / 2), int((__l_h - __t_h) / 2)),
                           __temp_base.split()[3])
    base.paste(luckypoint_frame, (38, 285), luckypoint_frame.split()[3])
    dataDraw.text((33, 380), "今日运气值", 'black', font2)

    # ys
    ys_frame = Image.open(IMAGE_PATH / 'jrys' / 'assets' /
                          'ys_list.png').convert('RGBA')
    base.paste(ys_frame, (150, 275), ys_frame.split()[3])
    font3 = ImageFont.truetype(titleFontName.__str__(), 20, encoding='utf-8')
    dataDraw.text((187, 278), "宜", 'black', font3)
    dataDraw.text((277, 278), "忌", 'black', font3)
    ys_do = []
    ys_notdo = []
    for i in range(8):
        item = _ys_ls_tmp.pop(random.randint(0, len(_ys_ls_tmp) - 1))
        if i % 2 == 0:
            ys_do.append(random.choice(item) if type(item) != str else item)
        else:
            ys_notdo.append(random.choice(item) if type(item) != str else item)
    font4 = ImageFont.truetype(titleFontName.__str__(), 16, encoding='utf-8')
    dataDraw.text((163, 312), '\n'.join(ys_do), 'black', font4)
    dataDraw.text((254, 312), '\n'.join(ys_notdo), 'black', font4)

    # Vtubers
    v_obj = vtuber_info
    v_name = v_obj['uname']
    v_url = f"https://space.bilibili.com/{v_obj['mid']}"
    v_info = f"粉丝数: {v_obj['follower']}"
    # v_qrcode = url_to_qrcode(v_url).resize((54, 54))
    vtuber_frame = Image.open(IMAGE_PATH / 'jrys' / 'assets' /
                              'Vtuber_Frame.png').convert('RGBA')

    if os.path.exists(IMAGE_PATH / 'vtb' / 'face' /
                      vtuber_info['face'].split('/')[-1]):
        vtb_avatar = Image.open(
            IMAGE_PATH / 'vtb' / 'face' /
            vtuber_info['face'].split('/')[-1]).convert('RGBA').resize(
                (150, 150))
    else:
        vtb_avatar = Image.open(IMAGE_PATH / 'vtb' / 'face' /
                                'default.jpg').convert('RGBA').resize(
                                    (150, 150))
    vtb_base = Image.new('RGBA', vtuber_frame.size, (0, 0, 0, 0))
    vtb_base.paste(vtb_avatar, (8, 33), vtb_avatar.split()[3])
    # vtb_base.paste(v_qrcode, (103, 127))
    vtb_base.paste(vtuber_frame, (0, 0), vtuber_frame.split()[3])
    dataDraw2 = ImageDraw.Draw(vtb_base)
    while font2.getsize(v_name)[0] > vtuber_frame.size[0] - 20:
        v_name = v_name[:-2] + '.'
    if v_name[-1] == '.':
        v_name += '..'
    dataDraw2.text((int(
        (vtb_base.size[0] - font2.getsize(v_name)[0]) / 2), 188), v_name,
                   'black', font2)
    dataDraw2.text((10, 7), "今日推荐Vtuber", 'black', font2)
    dataDraw2.text((int(
        (vtb_base.size[0] - font4.getsize(v_info)[0]) / 2), 220), v_info,
                   'black', font4)
    base.paste(vtb_base, (350, 165), vtb_base.split()[3])
    # base.show()
    return base.convert('RGB')


@Commands("今日运势")
async def jrys(api: BotAPI, message: Message, params: str = None):
    # seed
    _t = time.strftime("%Y-%m-%d", time.localtime())
    seed = f'{_t}-{message.author.id}'

    # avatar
    if not os.path.exists(
            IMAGE_PATH / 'user_avatar' / f'{message.author.id}.png'):
        await user_avatar_rounded(message.author.avatar, message.author.id)
    vtb_info = get_vtubers(seed=seed, return_type='dict')
    if not os.path.exists(
            IMAGE_PATH / 'vtb' / 'face' / vtb_info['face'].split('/')[-1]):
        try:
            await download_image(
                vtb_info['face'],
                IMAGE_PATH / 'vtb' / 'face' / vtb_info['face'].split('/')[-1])
        except Exception:
            pass
    frameid = None
    user_info = {
        'user_id': message.author.id,
        'nickname': message.author.username
    }
    final_images = [
        generate_jrys_graph(seed=seed,
                            user_info=user_info,
                            vtuber_info=vtb_info,
                            frame_id=frameid)
    ]
    warning = "*此模块仍在设计中"

    if 1:
        try:
            final_images.append(get_maimai_img(seed))
        except Exception:
            pass

    try:
        final_images.append(
            generate_chuni_graph_new(chuni_music_list.random(seed),
                                     'recommend').resize((1080, 608)))
    except Exception:
        pass

    if 1:
        try:
            final_images.append(
                generate_sekai_music_graph(pjsk_list.random(seed)))
        except Exception:
            pass

    if 1:
        try:
            final_images.append(generate_gbp_graph(
                gbp_total_list.random(seed)))
        except Exception:
            pass

    image_width = [x.size[0] for x in final_images]
    image_height = [x.size[1] for x in final_images]
    final_img = Image.new('RGB', (max(image_width), sum(image_height)),
                          (0, 0, 0, 0))
    __height = 0
    for _img in range(len(final_images)):
        final_img.paste(final_images[_img], (0, __height))
        __height += image_height[_img]
    final_bin = BytesIO()
    final_img.save(final_bin, 'jpeg', quality=80)
    await message.reply(file_image=final_bin.getvalue())
