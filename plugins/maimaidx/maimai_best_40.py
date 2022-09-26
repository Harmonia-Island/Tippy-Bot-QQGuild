# Author: xyb, Diving_Fish
import math
import os
import random
from typing import Dict, List, Optional

import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from configs.path import FONT_PATH, IMAGE_PATH
from models.maimaidx import MaimaiUserData
from utils.utils import circle_corner, user_avatar_rounded

from .maimaidx_music import total_list, all_plate_id
from .maimaidx_recommend import generate_recom_frame

scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')


class ChartInfo(object):

    def __init__(self, idNum: str, diff: int, tp: str, achievement: float,
                 ra: int, comboId: int, scoreId: int, fsId: int, title: str,
                 ds: float, lv: str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = ra
        self.comboId = comboId
        self.scoreId = scoreId
        self.fsId = fsId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    @classmethod
    def from_json(cls, data):
        rate = [
            'd', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss',
            'ssp', 'sss', 'sssp'
        ]
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fs = ['', 'fs', 'fsp', 'fsd', 'fsdp']
        try:
            fi = fc.index(data["fc"])
        except ValueError:
            fi = 4
        try:
            si = fs.index(data["fs"])
        except ValueError:
            si = 4
        return cls(idNum=total_list.by_title(data["title"]).id,
                   title=data["title"],
                   diff=data["level_index"],
                   ra=data["ra"],
                   ds=data["ds"],
                   comboId=fi,
                   scoreId=ri,
                   fsId=si,
                   lv=data["level"],
                   achievement=data["achievements"],
                   tp=data["type"])


class BestList(object):

    def __init__(self, size: int):
        self.data = []
        self.size = size

    def push(self, elem: ChartInfo, need_sort: bool = True):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        if need_sort:
            self.data.sort()
            self.data.reverse()
        while (len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


class DrawBest(object):

    def __init__(self,
                 sdBest: BestList,
                 dxBest: BestList,
                 userName: str,
                 playerRating: int,
                 musicRating: int,
                 userqq: int,
                 isHost: bool,
                 b50: bool,
                 userid: str,
                 plateid: int,
                 frameid: Optional[int] = None,
                 iconid: Optional[int] = None,
                 drawType: str = 'bp_old',
                 recomPic: Optional[list] = None):
        """
        说明：
            绘制bp列表
        参数：
            :param sdBest: 标准谱成绩列表
            :param dxBest: DX谱成绩列表
            :param userName: 昵称
            :param playerRating: 总分
            :param musicRating: 底分
            :param userqq: 用户QQ
            :param isHost: 是否为号主查询
            :param b50: 是否查询b50
            :param userid: 用户名
            :param plateid: 姓名框
        """
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userqq = userqq
        self.b50 = b50
        self.isHost = isHost
        self.userName = self._stringQ2B(userName)
        self.userid = userid
        self.iconid = iconid
        self.plateid = plateid
        self.frameid = frameid
        self.recomPic = recomPic
        self.drawType = drawType
        self.playerRating = playerRating
        self.musicRating = musicRating
        self.combo_status = 'APp'
        self.score_status = 'SSSp'
        self.rankRating = self.playerRating - self.musicRating
        self.min_ra = min(
            [computeRa(x.ds, x.achievement, self.b50) for x in self.sdBest])
        if self.b50:
            self.playerRating = 0
            for sd in sdBest:
                self.playerRating += computeRa(sd.ds, sd.achievement, True)
            if dxBest:
                for dx in dxBest:
                    self.playerRating += computeRa(dx.ds, dx.achievement, True)
        self.pic_dir = IMAGE_PATH / 'maimai' / 'assets'
        self.cover_dir = IMAGE_PATH / 'maimai' / 'cover'
        self.plate_dir = IMAGE_PATH / 'maimai' / 'plate'
        self.icon_dir = IMAGE_PATH / 'maimai' / 'icon'
        self.map_assets = IMAGE_PATH / 'maimai' / 'mapassets'
        if self.b50 or drawType == 'recommend':
            self.img = Image.new('RGB', (1080, 1535 + 295), (255, 255, 255))
            baseplate = Image.open(self.pic_dir /
                                   'b50_plate_new.png').convert('RGBA')
            _l = (0, 452)
        elif self.dxBest is None:
            self.img = Image.new('RGB', (1080, 1495), (255, 255, 255))
            baseplate = Image.open(self.pic_dir /
                                   'search_plate_new.png').convert('RGBA')
            _l = (0, 452)

        elif drawType == 'bp_new':
            self.img = Image.new('RGB', (1866, 1080), (255, 255, 255))
            baseplate = Image.open(self.pic_dir /
                                   'b40_plate_beta.png').convert('RGBA')
            _l = (0, 0)
        else:
            self.img = Image.new('RGB', (1080, 1595), (255, 255, 255))
            baseplate = Image.open(self.pic_dir /
                                   'b40_plate_new.png').convert('RGBA')
            _l = (0, 452)
        self.img.paste(baseplate, _l, baseplate)
        # imgFrame = Image.open(self.map_assets / 'UI_Frame_250745.png').convert('RGBA')
        if drawType != 'bp_new':
            imgFrame = Image.open(
                self.map_assets /
                'UI_Frame_{:0>6}.png'.format(self.frameid)).convert('RGBA')
            self.img.paste(imgFrame, (0, 0), imgFrame)
        if drawType == 'recommend':
            self.draw_recommend()
        else:
            if drawType == 'bp_new':
                self.ROWS_IMG = [2]
                if self.b50:
                    col = 8
                elif self.dxBest is None:
                    col = 9
                else:
                    col = 6
                for i in range(col):
                    self.ROWS_IMG.append(130 * i)
                self.COLOUMS_IMG = []

                _clm = 6
                for i in range(_clm):
                    self.COLOUMS_IMG.append(370 * i)
                for i in range(4):
                    self.COLOUMS_IMG.append(370 * i)
            else:
                self.ROWS_IMG = [2]
                if self.b50:
                    col = 8
                elif self.dxBest is None:
                    col = 9
                else:
                    col = 6
                for i in range(col):
                    # self.ROWS_IMG.append(130 + 96 * i)
                    self.ROWS_IMG.append(115 * i)
                self.COLOUMS_IMG = []

                _clm = 6
                for i in range(_clm):
                    self.COLOUMS_IMG.append(18 + 210 * i)
                for i in range(4):
                    self.COLOUMS_IMG.append(18 + 210 * i)
            self.draw()

    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1),
            (159, 0),
            (687, 1),
            (710, 0),
            (711, 1),
            (727, 0),
            (733, 1),
            (879, 0),
            (1154, 1),
            (1161, 0),
            (4347, 1),
            (4447, 2),
            (7467, 1),
            (7521, 0),
            (8369, 1),
            (8426, 0),
            (9000, 1),
            (9002, 2),
            (11021, 1),
            (12350, 2),
            (12351, 1),
            (12438, 2),
            (12442, 0),
            (19893, 2),
            (19967, 1),
            (55203, 2),
            (63743, 1),
            (64106, 2),
            (65039, 1),
            (65059, 0),
            (65131, 2),
            (65279, 1),
            (65376, 2),
            (65500, 1),
            (65510, 2),
            (120831, 1),
            (262141, 2),
            (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _coloumWidth(self, s: str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s: str, len: int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)

    def _resizePic(self, img: Image.Image, time: float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))

    def _findRaPic(self) -> str:
        num = '10'
        if self.playerRating < 1000:
            num = '01'
        elif self.playerRating < 2000:
            num = '02'
        elif self.playerRating < (3000 if not self.b50 else 4000):
            num = '03'
        elif self.playerRating < (4000 if not self.b50 else 7000):
            num = '04'
        elif self.playerRating < (5000 if not self.b50 else 10000):
            num = '05'
        elif self.playerRating < (6000 if not self.b50 else 12000):
            num = '06'
        elif self.playerRating < (7000 if not self.b50 else 13000):
            num = '07'
        elif self.playerRating < (8000 if not self.b50 else 14500):
            num = '08'
        elif self.playerRating < (8500 if not self.b50 else 15000):
            num = '09'
        return f'UI_CMN_DXRating_S_{num}.png'

    def _findRankingPic(self) -> str:
        return f'Ranking_{self.rankRating}.png'

    def _drawRating(self, ratingBaseImg: Image.Image):
        COLOUMS_RATING = [86, 100, 115, 130, 145]
        theRa = self.playerRating
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(
                self.pic_dir / f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i] - 2, 9),
                                mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    def _drawBestList_old(self, img: Image.Image, sdBest: BestList,
                          dxBest: BestList):
        itemW = 164
        itemH = 88
        # Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (217, 197, 233)]
        # levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        fsPic = ' FS FSp FSD FSDp'.split(' ')
        titleFontName = str(FONT_PATH / 'adobe_simhei.otf')
        for num in range(0, len(sdBest)):
            if True:
                i = num // 5
                j = num % 5
            chartInfo = sdBest[num]

            # mark combo
            if self.combo_status is not None and chartInfo.comboId != 0:
                if comboPic.index(self.combo_status) > chartInfo.comboId:
                    self.combo_status = comboPic[chartInfo.comboId]
            else:
                self.combo_status = None

            # mark score
            if self.score_status is not None and chartInfo.scoreId > 7:
                if rankPic.index(self.score_status) > chartInfo.scoreId:
                    self.score_status = rankPic[chartInfo.scoreId]
            else:
                self.score_status = None

            pngPath = self.cover_dir / f'{chartInfo.idNum}.png'
            if not os.path.exists(pngPath):
                pngPath = self.cover_dir / 'default.png'
            temp = Image.open(pngPath).convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW,
                              (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: p * 0.72)

            # temp = self._circle_corner(temp, 25)
            tempDraw = ImageDraw.Draw(temp)
            # tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 13) + '...'

            # Music Type
            mapType = chartInfo.tp
            typeImg = Image.open(self.pic_dir /
                                 f'{mapType}.png').convert('RGBA')
            temp.paste(typeImg, (8, 8), typeImg.split()[3])

            # Map Difficulty
            mapDiff = chartInfo.diff
            mapDiff = diffs[mapDiff].replace(':', '')
            diffImg = Image.open(self.pic_dir /
                                 f'{mapDiff}.png').convert('RGBA')
            temp.paste(diffImg, (52, 8), diffImg.split()[3])

            # tempDraw.text((8, 8), title, 'white', font)
            tempDraw.text((8, 28), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')

            # tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
            tempDraw.text((7, 48), f'{"%.4f" % chartInfo.achievement}%',
                          'white', font)
            rankImg = Image.open(
                self.pic_dir /
                f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert(
                    'RGBA')
            rankImg = self._resizePic(rankImg, 0.49)
            temp.paste(rankImg, (75, 60), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(
                    self.pic_dir /
                    f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png'
                ).convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.7)
                # temp.paste(comboImg, (119, 27), comboImg.split()[3])
                temp.paste(comboImg, (130, 55), comboImg.split()[3])

            if chartInfo.fsId:
                fsImg = Image.open(
                    self.pic_dir /
                    f'UI_MSS_MBase_Icon_{fsPic[chartInfo.fsId]}_S.png'
                ).convert('RGBA')
                fsImg = self._resizePic(fsImg, 0.7)
                # temp.paste(comboImg, (119, 27), comboImg.split()[3])
                temp.paste(fsImg, (130, 25), fsImg.split()[3])

            font = ImageFont.truetype(str(FONT_PATH / 'adobe_simhei.otf'),
                                      12,
                                      encoding='utf-8')
            # tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
            tempDraw.text((
                8, 66
            ), f'{chartInfo.ds} -> {chartInfo.ra if not self.b50 else computeRa(chartInfo.ds, chartInfo.achievement, True)}',
                          'white', font)
            font = ImageFont.truetype(str(FONT_PATH / 'adobe_simhei.otf'),
                                      18,
                                      encoding='utf-8')

            # tempDraw.text((8, 60), f'#{num + 1} ({mapType})', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: p * 0.8)
            recBase = circle_corner(recBase, 15, False)

            recBase = self._resizePic(recBase, 1.2)
            temp = self._resizePic(temp, 1.2)
            img.paste(recBase, (self.COLOUMS_IMG[j] + 5,
                                self.ROWS_IMG[i + 1] + 5 + 452 + 100),
                      mask=recBase.split()[3])
            temp = circle_corner(temp, 15, False)
            img.paste(temp, (self.COLOUMS_IMG[j] + 4,
                             self.ROWS_IMG[i + 1] + 4 + 452 + 100),
                      mask=temp.split()[3])
        for num in range(len(sdBest), sdBest.size):
            # i = num // 5 if not self.b50 else num // 7
            # if self.b50 or not self.dxBest:
            #     i = num // 7
            #     j = num % 7
            # else:
            if True:
                i = num // 5
                j = num % 5
            # j = num % 5 if not self.b50 else num % 7
            temp = Image.open(self.cover_dir / 'default.png').convert('RGBA')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW,
                              (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            temp = circle_corner(temp, 15, False)
            # print(f'j: {j} i: {i} len:{len(self.COLOUMS_IMG)}\n')
            temp = self._resizePic(temp, 1.2)
            img.paste(temp, (self.COLOUMS_IMG[j] + 4,
                             self.ROWS_IMG[i + 1] + 4 + 452 + 100),
                      mask=temp.split()[3])
        if self.b50:
            dxspace = 1075 + 395
        else:
            dxspace = 1235
        if dxBest is not None:
            for num in range(0, len(dxBest)):
                # i = num // 3
                # j = num % 3
                i = num // 5
                j = num % 5
                chartInfo = dxBest[num]
                if self.combo_status is not None and chartInfo.comboId != 0:
                    if comboPic.index(self.combo_status) > chartInfo.comboId:
                        self.combo_status = comboPic[chartInfo.comboId]
                else:
                    self.combo_status = None

                # mark score
                if self.score_status is not None and chartInfo.scoreId > 7:
                    if rankPic.index(self.score_status) > chartInfo.scoreId:
                        self.score_status = rankPic[chartInfo.scoreId]
                else:
                    self.score_status = None
                pngPath = self.cover_dir / f'{int(chartInfo.idNum)}.jpg'
                if not os.path.exists(pngPath):
                    pngPath = self.cover_dir / f'{int(chartInfo.idNum)}.png'
                if not os.path.exists(pngPath):
                    pngPath = self.cover_dir / 'default.png'
                temp = Image.open(pngPath).convert('RGB')
                temp = self._resizePic(temp, itemW / temp.size[0])
                temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW,
                                  (temp.size[1] + itemH) / 2))
                temp = temp.filter(ImageFilter.GaussianBlur(3))
                temp = temp.point(lambda p: p * 0.72)

                tempDraw = ImageDraw.Draw(temp)
                # tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
                font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
                title = chartInfo.title
                if self._coloumWidth(title) > 15:
                    title = self._changeColumnWidth(title, 13) + '...'

                # Music Type
                mapType = chartInfo.tp
                typeImg = Image.open(self.pic_dir /
                                     f'{mapType}.png').convert('RGBA')
                temp.paste(typeImg, (8, 8), typeImg.split()[3])

                # Map Difficulty
                mapDiff = chartInfo.diff
                mapDiff = diffs[mapDiff].replace(':', '')
                diffImg = Image.open(self.pic_dir /
                                     f'{mapDiff}.png').convert('RGBA')
                temp.paste(diffImg, (52, 8), diffImg.split()[3])

                # tempDraw.text((8, 8), title, 'white', font)
                tempDraw.text((8, 28), title, 'white', font)
                font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')

                # tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
                tempDraw.text((7, 48), f'{"%.4f" % chartInfo.achievement}%',
                              'white', font)
                rankImg = Image.open(
                    self.pic_dir /
                    f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert(
                        'RGBA')
                # rankImg = self._resizePic(rankImg, 0.3)
                rankImg = self._resizePic(rankImg, 0.49)
                # temp.paste(rankImg, (88, 28), rankImg.split()[3])
                # temp.paste(rankImg, (88, 48), rankImg.split()[3])
                temp.paste(rankImg, (75, 60), rankImg.split()[3])
                if chartInfo.comboId:
                    comboImg = Image.open(
                        self.pic_dir /
                        f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png'
                    ).convert('RGBA')
                    comboImg = self._resizePic(comboImg, 0.7)
                    # temp.paste(comboImg, (119, 27), comboImg.split()[3])
                    temp.paste(comboImg, (130, 55), comboImg.split()[3])

                if chartInfo.fsId:
                    fsImg = Image.open(
                        self.pic_dir /
                        f'UI_MSS_MBase_Icon_{fsPic[chartInfo.fsId]}_S.png'
                    ).convert('RGBA')
                    fsImg = self._resizePic(fsImg, 0.7)
                    # temp.paste(comboImg, (119, 27), comboImg.split()[3])
                    temp.paste(fsImg, (130, 25), fsImg.split()[3])

                font = ImageFont.truetype(str(FONT_PATH / 'adobe_simhei.otf'),
                                          12,
                                          encoding='utf-8')
                # tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
                tempDraw.text((
                    8, 66
                ), f'{chartInfo.ds} -> {chartInfo.ra if not self.b50 else computeRa(chartInfo.ds, chartInfo.achievement, True)}',
                              'white', font)
                font = ImageFont.truetype(str(FONT_PATH / 'adobe_simhei.otf'),
                                          18,
                                          encoding='utf-8')
                # tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

                recBase = Image.new('RGBA', (itemW, itemH), 'black')
                recBase = recBase.point(lambda p: p * 0.8)
                recBase = circle_corner(recBase, 15, False)

                recBase = self._resizePic(recBase, 1.2)
                temp = self._resizePic(temp, 1.2)

                img.paste(recBase, (self.COLOUMS_IMG[j] + 5,
                                    self.ROWS_IMG[i + 1] + 5 + dxspace),
                          mask=recBase.split()[3])
                temp = circle_corner(temp, 15, False)
                img.paste(temp, (self.COLOUMS_IMG[j] + 4,
                                 self.ROWS_IMG[i + 1] + 4 + dxspace),
                          mask=temp.split()[3])
            for num in range(len(dxBest), dxBest.size):
                i = num // 5
                j = num % 5
                temp = Image.open(self.cover_dir /
                                  'default.png').convert('RGBA')
                temp = self._resizePic(temp, itemW / temp.size[0])
                temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW,
                                  (temp.size[1] + itemH) / 2))
                temp = temp.filter(ImageFilter.GaussianBlur(1))
                temp = self._resizePic(temp, 1.2)
                img.paste(temp, (self.COLOUMS_IMG[j] + 4,
                                 self.ROWS_IMG[i + 1] + 4 + dxspace),
                          mask=temp.split()[3])

    def _drawBestCard(self, num, titleFontName, BestList, comboPic, rankPic,
                      fsPic, isNew):
        titleFontName = str(FONT_PATH / 'UDDigiKyokashoN-B.ttc')
        chartInfo = BestList[num]
        musicInfo = total_list.by_id(chartInfo.idNum)

        # mark combo
        if self.combo_status is not None and chartInfo.comboId != 0:
            if comboPic.index(self.combo_status) > chartInfo.comboId:
                self.combo_status = comboPic[chartInfo.comboId]
        else:
            self.combo_status = None

        # mark score
        if self.score_status is not None and chartInfo.scoreId > 7:
            if rankPic.index(self.score_status) > chartInfo.scoreId:
                self.score_status = rankPic[chartInfo.scoreId]
        else:
            self.score_status = None

        # begin chart generate
        pngPath = self.cover_dir / f'{chartInfo.idNum}.png'
        if not os.path.exists(pngPath):
            pngPath = self.cover_dir / 'default.png'
        temp = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                          'new_single_shadow.png').convert('RGBA')
        if chartInfo.scoreId > 11:
            __tempBase = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                                    'new_single_SSS.png').convert('RGBA')
        elif chartInfo.scoreId > 9:
            __tempBase = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                                    'new_single_SS.png').convert('RGBA')
        elif chartInfo.scoreId > 7:
            __tempBase = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                                    'new_single_S.png').convert('RGBA')
        else:
            __tempBase = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                                    'new_single.png').convert('RGBA')
        tempBase_w, tempBase_h = __tempBase.size
        tempBase = Image.new('RGBA', (tempBase_w, tempBase_h), (0, 0, 0, 0))
        cover = Image.open(pngPath).convert('RGBA').resize((108, 108))
        tempBase.paste(cover, (217, 0))
        tempBase.paste(__tempBase, (0, 0), __tempBase.split()[3])
        tempBase = circle_corner(tempBase, 10, None)
        if isNew:
            _New = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                              'new.png').convert('RGBA')
            tempBase.paste(_New, (253, 82), _New.split()[3])

        tempBaseDraw = ImageDraw.Draw(tempBase)
        title = chartInfo.title
        fontsize = 22
        font = ImageFont.truetype(titleFontName, fontsize, encoding='utf-8')
        title_w, title_h = font.getsize(title)
        while title_w > 190:
            fontsize -= 1
            font = ImageFont.truetype(titleFontName,
                                      fontsize,
                                      encoding='utf-8')
            title_w, _ = font.getsize(title)
            if fontsize < 18:
                break
        if fontsize < 18:
            while title_w > 190:
                title = title[:-1]
                font = ImageFont.truetype(titleFontName,
                                          fontsize,
                                          encoding='utf-8')
                title_w, _ = font.getsize(title)
        tempBaseDraw.text((22, 10), title, 'black', font)

        # Music Genre
        genre = musicInfo.genre
        genre_img = Image.open(IMAGE_PATH / 'maimai' / 'assets' /
                               f'{genre}_S.png').convert('RGBA')
        tempBase.paste(genre_img, (142, 40), genre_img.split()[3])

        # Music Type
        mapType = chartInfo.tp
        if mapType == 'DX':
            typeImg = Image.new('RGB', (5, 43), '#ff9c00')
        else:
            typeImg = Image.new('RGB', (5, 43), '#08a9ff')

        tempBase.paste(typeImg, (8, 11))

        # Map Difficulty
        mapDiff = chartInfo.diff
        _diffColor = ['#00ff3c', '#fcff00', '#ff1a1a', '#dd00ff', '#f090ff']
        diffImg = Image.new('RGB', (5, 43), _diffColor[mapDiff])
        tempBase.paste(diffImg, (8, 54))

        font = ImageFont.truetype(titleFontName, 35, encoding='utf-8')
        achievement = f'{"%.4f" % chartInfo.achievement}'.split(".")
        tempBaseDraw.text((20, 37), f'{achievement[0]}.', _diffColor[mapDiff],
                          font)
        _p_w, _ = font.getsize(f'{achievement[0]}.')
        font = ImageFont.truetype(titleFontName, 22, encoding='utf-8')
        tempBaseDraw.text((20 + _p_w, 48), f'{achievement[1]}',
                          _diffColor[mapDiff], font)

        rankImg = Image.open(
            self.pic_dir /
            f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
        rankImg = self._resizePic(rankImg, 0.5)
        tempBase.paste(rankImg, (20, 76), rankImg.split()[3])
        if chartInfo.comboId:
            comboImg = Image.open(
                self.pic_dir /
                f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png'
            ).convert('RGBA').resize((30, 30))
            tempBase.paste(comboImg, (80, 73), comboImg.split()[3])

        if chartInfo.fsId:
            fsImg = Image.open(
                self.pic_dir /
                f'UI_MSS_MBase_Icon_{fsPic[chartInfo.fsId]}_S.png').convert(
                    'RGBA').resize((30, 30))
            temp.paste(fsImg, (110, 73), fsImg.split()[3])

        font = ImageFont.truetype(titleFontName, 18, encoding='utf-8')
        # tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
        _song_ra = chartInfo.ra if not self.b50 else computeRa(
            chartInfo.ds, chartInfo.achievement, True)
        tempBaseDraw.text((145, 81), f'{chartInfo.ds}', _diffColor[mapDiff],
                          font)
        tempBaseDraw.text((182, 83), '>', '#007eff', font)
        font = ImageFont.truetype(titleFontName, 26, encoding='utf-8')

        tempBaseDraw.text((192, 77), f'{_song_ra}', '#ff0000', font)

        # tempDraw.text((8, 60), f'#{num + 1} ({mapType})', 'white', font)

        temp.paste(tempBase, (20, 20), tempBase.split()[3])

        return temp

    def _drawBestList(self, img: Image.Image, sdBest: BestList,
                      dxBest: BestList):
        itemW = 325
        itemH = 108
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        fsPic = ' FS FSp FSD FSDp'.split(' ')
        titleFontName = str(FONT_PATH / 'UDDigiKyokashoN-B.ttc')
        for num in range(0, len(sdBest)):
            i = num // 5
            j = num % 5
            temp = self._drawBestCard(num=num,
                                      titleFontName=titleFontName,
                                      BestList=sdBest,
                                      comboPic=comboPic,
                                      rankPic=rankPic,
                                      fsPic=fsPic,
                                      isNew=False)
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1]),
                      mask=temp.split()[3])
            dxspace = self.ROWS_IMG[i + 1] + 130
        # for num in range(len(sdBest), sdBest.size):
        #     i = num // 5
        #     j = num % 5
        #     temp = Image.open(self.cover_dir / 'default.png').convert('RGBA')
        #     temp = self._resizePic(temp, itemW / temp.size[0])
        #     temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW,
        #                       (temp.size[1] + itemH) / 2))
        #     temp = temp.filter(ImageFilter.GaussianBlur(1))
        #     temp = circle_corner(temp, 15, False)
        #     # print(f'j: {j} i: {i} len:{len(self.COLOUMS_IMG)}\n')
        #     temp = self._resizePic(temp, 1.2)
        #     img.paste(temp, (self.COLOUMS_IMG[j] + 4,
        #                      self.ROWS_IMG[i + 1] + 4 + 452 + 100),
        #               mask=temp.split()[3])
        if dxBest is not None:
            for num in range(0, len(dxBest)):
                i = num // 5
                j = num % 5
                temp = self._drawBestCard(num=num,
                                          titleFontName=titleFontName,
                                          BestList=dxBest,
                                          comboPic=comboPic,
                                          rankPic=rankPic,
                                          fsPic=fsPic,
                                          isNew=True)
                img.paste(temp, (self.COLOUMS_IMG[j] + 4,
                                 self.ROWS_IMG[i + 1] + 4 + dxspace),
                          mask=temp.split()[3])
            # for num in range(len(dxBest), dxBest.size):
            #     i = num // 5
            #     j = num % 5
            #     temp = Image.open(self.cover_dir /
            #                       'default.png').convert('RGBA')
            #     temp = self._resizePic(temp, itemW / temp.size[0])
            #     temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW,
            #                       (temp.size[1] + itemH) / 2))
            #     temp = temp.filter(ImageFilter.GaussianBlur(1))
            #     temp = self._resizePic(temp, 1.2)
            #     img.paste(temp, (self.COLOUMS_IMG[j] + 4,
            #                      self.ROWS_IMG[i + 1] + 4 + dxspace),
            #               mask=temp.split()[3])

    def _draw_name_plate(self, img):
        userPlate = Image.open(
            self.map_assets /
            'UI_Plate_{:0>6}.png'.format(self.plateid)).convert('RGBA')

        ratingBaseImg = Image.open(self.pic_dir /
                                   self._findRaPic()).convert('RGBA')
        ratingBaseImg = self._drawRating(ratingBaseImg)
        userPlate.paste(ratingBaseImg, (113, 6), mask=ratingBaseImg.split()[3])

        if self.iconid is not None:
            userAvater = Image.open(
                self.map_assets /
                'UI_Icon_{:0>6}.png'.format(self.iconid)).convert('RGBA')
            userAvater = userAvater.resize((94, 94))
            userPlate.paste(userAvater, (12, 10), mask=userAvater.split()[3])
        elif os.path.exists(IMAGE_PATH / 'user_avatar' / f'{self.userqq}.png'):
            userAvater = Image.open(
                IMAGE_PATH / 'user_avatar' /
                f'{self.userqq}.png').convert('RGBA').resize((94, 94))
            userPlate.paste(userAvater, (12, 10), mask=userAvater.split()[3])
        else:
            userAvater = Image.open(
                IMAGE_PATH / 'user_avatar' /
                'default_avatar.png').convert('RGBA').resize((94, 94))
            userPlate.paste(userAvater, (12, 10), mask=userAvater.split()[3])

        if self.iconid is None:
            avatarFrame = Image.open(
                IMAGE_PATH / 'user_avatar' /
                'avatar_frame.png').convert('RGBA').resize((94, 94))
            userPlate.paste(avatarFrame, (12, 10), mask=avatarFrame.split()[3])

        namePlateImg = Image.open(self.pic_dir /
                                  'UI_TST_PlateMask.png').convert('RGBA')
        namePlateImg = namePlateImg.resize((268, 35))
        namePlateDraw = ImageDraw.Draw(namePlateImg)
        font1 = ImageFont.truetype(str(FONT_PATH / 'msyh.ttc'),
                                   24,
                                   encoding='unic')
        namePlateDraw.text((14, 0), ' '.join(list(self.userName)), 'black',
                           font1)
        userPlate.paste(namePlateImg, (114, 46), mask=namePlateImg.split()[3])

        if self._findRankingPic():
            rankingBaseImg = Image.open(self.pic_dir /
                                        self._findRankingPic()).convert('RGBA')
            rankingBaseImg = self._drawRating(rankingBaseImg)
            rankingBaseImg = rankingBaseImg.resize((81, 34))
            userPlate.paste(rankingBaseImg, (297, 45),
                            mask=rankingBaseImg.split()[3])

        shougouImg = Image.open(
            self.pic_dir /
            'UI_CMN_Shougou_Rainbow.png').convert('RGBA').resize((272, 30))
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype(str(FONT_PATH / 'adobe_simhei.otf'),
                                   13,
                                   encoding='utf-8')
        if self.b50:
            playCountInfo = 'Simulation of UNiVERSE Rating'
        # elif not self.dxBest:
        #     playCountInfo = 'Search result'
        else:
            playCountInfo = f'底分: {self.musicRating} + 段位分: {self.rankRating}'
        shougouImgW, shougouImgH = shougouImg.size
        playCountInfoW, playCountInfoH = shougouDraw.textsize(
            playCountInfo, font2)
        textPos = ((shougouImgW - playCountInfoW -
                    font2.getoffset(playCountInfo)[0]) / 2, 5)
        shougouDraw.text((textPos[0] - 1, textPos[1]), playCountInfo, 'black',
                         font2)
        shougouDraw.text((textPos[0] + 1, textPos[1]), playCountInfo, 'black',
                         font2)
        shougouDraw.text((textPos[0], textPos[1] - 1), playCountInfo, 'black',
                         font2)
        shougouDraw.text((textPos[0], textPos[1] + 1), playCountInfo, 'black',
                         font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] - 1), playCountInfo,
                         'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] - 1), playCountInfo,
                         'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] + 1), playCountInfo,
                         'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] + 1), playCountInfo,
                         'black', font2)
        shougouDraw.text(textPos, playCountInfo, 'white', font2)
        userPlate.paste(shougouImg, (111, 80), mask=shougouImg.split()[3])
        img.paste(userPlate, (30, 30), mask=userPlate.split()[3])

    def _draw_score_table(self, img):
        # Score table
        if self.dxBest is not None:
            table_base_x = 50
            table_base_y = 67
            table_space_x = 112
            table_space_y = 37
            TABLE_POS = {98: 1, 99: 2, 99.5: 3, 100: 4, 100.5: 5}
            scoreTableImg = Image.open(self.pic_dir /
                                       'RatingTable.png').convert('RGBA')
            scoreTableDraw = ImageDraw.Draw(scoreTableImg)
            _font2 = ImageFont.truetype(str(FONT_PATH / 'adobe_simhei.otf'),
                                        24,
                                        encoding='utf-8')
            recommend_data = getBaseRating(self.min_ra, self.b50)
            r_top = min(recommend_data) + 2.3
            for x in recommend_data.copy():
                if x > r_top:
                    recommend_data.pop(x)
            if len(recommend_data) > 10:
                temp_entry = recommend_data.copy()
                for entry in enumerate(temp_entry):
                    if entry[0] % (len(temp_entry) // 5) != 0:
                        del recommend_data[entry[1]]
            __cnt = 0
            for _ds in enumerate(recommend_data):
                __cnt += 1
                scoreTableDraw.text(
                    (table_base_x, table_base_y + _ds[0] * table_space_y),
                    f'{_ds[1]}', 'white', _font2)
                for __score in recommend_data[_ds[1]]:
                    scoreTableDraw.text(
                        (table_base_x + TABLE_POS[__score[0]] * table_space_x,
                         table_base_y + _ds[0] * table_space_y),
                        f'{__score[1]}', 'black', _font2)
                if __cnt >= 5:
                    break
            scoreTableImg = scoreTableImg.resize((712, 344))
            img.paste(scoreTableImg, (25, 165), mask=scoreTableImg.split()[3])

        authorBoardImg = Image.open(self.pic_dir /
                                    'bytippy.png').convert('RGBA')

        img.paste(authorBoardImg, (915, 390), mask=authorBoardImg.split()[3])

        if self.drawType not in ['bp_new', 'recommend']:
            if self.dxBest is not None:
                latest_title = Image.open(self.pic_dir /
                                          'Latest.png').convert('RGBA').resize(
                                              (450, 75))
                not_latest_title = Image.open(
                    self.pic_dir / 'Not_Latest.png').convert('RGBA').resize(
                        (450, 75))
                if self.b50:
                    img.paste(latest_title, (315, 1380),
                              mask=latest_title.split()[3])
                else:
                    img.paste(latest_title, (315, 1145),
                              mask=latest_title.split()[3])
                img.paste(not_latest_title, (315, 465),
                          mask=not_latest_title.split()[3])
            elif self.drawType != 'recommend':
                search_title = Image.open(
                    self.pic_dir / 'search_title.png').convert('RGBA').resize(
                        (450, 75))
                img.paste(search_title, (315, 465),
                          mask=search_title.split()[3])

        if self.drawType != 'recommend':
            if self.combo_status is not None:
                comboimg = Image.open(
                    self.pic_dir /
                    f'UI_MSS_Allclear_Icon_{self.combo_status}.png').convert(
                        'RGBA')
                comboimg = comboimg.resize((112, 140))
                img.paste(comboimg, (780, 18), mask=comboimg.split()[3])
            if self.score_status is not None:
                scoreimg = Image.open(
                    self.pic_dir /
                    f'UI_MSS_Allclear_Icon_{self.score_status}.png').convert(
                        'RGBA')
                if self.combo_status is None:
                    img.paste(scoreimg, (770, 18), mask=scoreimg.split()[3])
                else:
                    img.paste(scoreimg, (880, 18), mask=scoreimg.split()[3])

    def draw(self):
        if self.drawType != 'bp_new':
            self._draw_name_plate(self.img)
            otomotachiImg = Image.open(
                self.pic_dir / 'UI_CMN_Class_S_25.png').convert('RGBA').resize(
                    (94, 56))
            self.img.paste(otomotachiImg, (315, 20),
                           mask=otomotachiImg.split()[3])
        if self.drawType == 'bp_new':
            self._drawBestList(self.img, self.sdBest, self.dxBest)
        else:
            self._drawBestList_old(self.img, self.sdBest, self.dxBest)
            self._draw_score_table(self.img)

    def draw_recommend(self):
        self._draw_name_plate(self.img)
        otomotachiImg = Image.open(
            self.pic_dir / 'UI_CMN_Class_S_25.png').convert('RGBA').resize(
                (94, 56))
        self.img.paste(otomotachiImg, (315, 20), mask=otomotachiImg.split()[3])
        if self.userqq is not None:
            self._draw_score_table(self.img)
            pos_y = 480
            for t in self.recomPic:
                tmp = generate_recom_frame(t[0], t[1], t[2]).resize(
                    (1027, 225))
                self.img.paste(tmp, (25, pos_y), mask=tmp.split()[3])
                pos_y += 260
        # self.img.show()

    def getDir(self):
        return self.img


def getBaseRating(baseRating: int, newAlogrithm=False):
    _i = 1.0
    ach_ls = [98, 99, 99.5, 100, 100.5]
    r_ls: List[tuple] = {}
    while _i < 15:
        for ach in ach_ls:
            _ra = computeRa(_i, ach, newAlogrithm)
            if _ra > baseRating:
                _ii = float('{:.1f}'.format(_i))
                if _ii in r_ls:
                    r_ls[_ii].append((ach, _ra))
                else:
                    r_ls[_ii] = [(ach, _ra)]
        _i += 0.1
    return r_ls


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


async def generate(payload: Dict,
                   author: str,
                   isHost: bool,
                   isBeta: bool = False):
    async with aiohttp.request(
            "POST",
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        b50 = False
        if 'b50' in payload:
            b50 = True
            sd_best = BestList(35)
        else:
            sd_best = BestList(25)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        for c in sd:
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_best.push(ChartInfo.from_json(c))
        if obj['nickname'] == 'MaxScore':
            _nickname = '理论值'
        else:
            _nickname = obj['nickname']
        if isHost:
            await user_avatar_rounded(author.avatar, author.id)
        custom_info = await MaimaiUserData.get_info(obj['username'])
        # plate
        plate_id = 100702
        icon_id = None
        frame_id = 105601
        if obj['user_data']:
            if obj['user_data']['plateId']:
                if f'{plate_id}.png' in os.listdir(IMAGE_PATH / 'maimai' /
                                                   'plate'):
                    plate_id = int(obj['user_data']['plateId'])
        else:
            if obj['plate'] != "":
                if obj['plate'] in all_plate_id:
                    plate_id = all_plate_id[obj['plate']]
        if custom_info:
            if custom_info.plate:
                plate_id = custom_info.plate
            # icon
            if custom_info.icon:
                icon_id = custom_info.icon
            if custom_info.frame:
                frame_id = custom_info.frame
            else:
                user_profile = None
                if user_profile is not None:
                    frame_id = user_profile.frameid
        beta = 'bp_new' if isBeta else 'bp_old'
        pic = DrawBest(sdBest=sd_best,
                       dxBest=dx_best,
                       userName=_nickname,
                       playerRating=obj["rating"] + obj["additional_rating"],
                       musicRating=obj["rating"],
                       userqq=author.id,
                       isHost=isHost,
                       b50=b50,
                       userid=obj['username'],
                       plateid=plate_id,
                       frameid=frame_id,
                       iconid=icon_id,
                       drawType=beta).getDir().convert('RGB')
        return pic, 0


async def get_max_min(payload: Dict) -> tuple:
    async with aiohttp.request(
            "POST",
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json=payload) as resp:
        if resp.status == 400:
            return (None, 400)
        if resp.status == 403:
            return (None, 403)
        # sd_best = BestList(25)
        # dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        ds_list = []
        if len(sd) == 0:
            return (0, 0)
        for i in dx:
            ds_list.append(i['ds'])
        for i in sd:
            ds_list.append(i['ds'])
        ds_max = max(ds_list)
        ds_min = min(ds_list)
        # max
        if ds_max > 14.8:
            ds_max = 15.0
        elif ds_max > 13.5:
            ds_max += 0.2
        elif ds_max > 13.0:
            ds_max += 0.3
        elif ds_max > 12.0:
            ds_max += 0.5
        elif ds_max - 3 <= ds_min:
            ds_max += 4
        else:
            ds_max += 1.0
        return (ds_min, ds_max)


async def get_user_info(payload: Dict) -> Dict:
    async with aiohttp.request(
            "POST",
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json=payload) as resp:
        if resp.status == 400:
            return {'error': True, 'status': 400}
        elif resp.status == 403:
            return {'error': True, 'status': 403}
        obj = await resp.json()
    return {
        'username': obj['username'],
        'nickname': obj['nickname'],
        'rating': obj['rating'],
        'additional_rating': obj['additional_rating'],
        'error': False,
        'plate': obj['plate'],
        'user_data': obj['user_data']
    }


plate_to_version = {
    '初': 'maimai',
    '真': 'maimai PLUS',
    '超': 'maimai GreeN',
    '檄': 'maimai GreeN PLUS',
    '橙': 'maimai ORANGE',
    '暁': 'maimai ORANGE PLUS',
    '晓': 'maimai ORANGE PLUS',
    '桃': 'maimai PiNK',
    '櫻': 'maimai PiNK PLUS',
    '樱': 'maimai PiNK PLUS',
    '紫': 'maimai MURASAKi',
    '菫': 'maimai MURASAKi PLUS',
    '堇': 'maimai MURASAKi PLUS',
    '白': 'maimai MiLK',
    '雪': 'MiLK PLUS',
    '輝': 'maimai FiNALE',
    '辉': 'maimai FiNALE',
    '熊': 'maimai でらっくす',
    '華': 'maimai でらっくす PLUS',
    '华': 'maimai でらっくす PLUS',
    '爽': 'maimai でらっくす Splash',
    '煌': 'maimai でらっくす Splash',
    '宙': 'maimai でらっくす Splash PLUS'
}


async def get_player_plate(payload: Dict):
    async with aiohttp.request(
            "POST",
            "https://www.diving-fish.com/api/maimaidxprober/query/plate",
            json=payload) as resp:
        if resp.status == 400:
            return None, 400
        elif resp.status == 403:
            return None, 403
        plate_data = await resp.json()
        return plate_data, 0


async def get_recommend(payload: Dict) -> tuple:
    async with aiohttp.request(
            "POST",
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json=payload) as resp:
        if resp.status == 400:
            return (400, None, None)
        if resp.status == 403:
            return (403, None, None)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        music_ls = []
        nall_sssp = False
        if len(dx) != 0 and len(sd) != 0:
            for u in dx:
                if u['achievements'] < 100.5:
                    # print(u)
                    nall_sssp = True
                    break
            for u in sd:
                if u['achievements'] < 100.5:
                    # print(u)
                    nall_sssp = True
                    break
            # print(nall_sssp)

            if random.random() > 0.7 and nall_sssp:
                for i in dx:
                    if i['achievements'] < 100.5:
                        music_ls.append((i['achievements'], i["song_id"],
                                         i['level_index']))
                for i in sd:
                    if i['achievements'] < 100.5:
                        music_ls.append((i['achievements'], i["song_id"],
                                         i['level_index']))
            else:
                ate_dict = {}
                achievement_ls = [97, 98, 99, 99.5, 100, 100.5]
                for j in dx:
                    ate_dict[str(j['song_id']) +
                             str('{:.1f}'.format(j['ds']))] = j['achievements']
                for j in sd:
                    ate_dict[str(j['song_id']) +
                             str('{:.1f}'.format(j['ds']))] = j['achievements']
                # print(ate_dict)
                max_min_ds = await get_max_min(payload)
                # print(max_min_ds)
                if (max_min_ds[0]
                        is not None) and (max_min_ds[1] - max_min_ds[0] > 0.3):
                    min_ra = sd[-1]['ra']
                    # min_ra = min(dx[-1]['ra'], sd[-1]['ra'])
                    result_set = []
                    music_data = total_list.filter(ds=(float(max_min_ds[0]),
                                                       float(max_min_ds[1])))
                    for music in sorted(music_data,
                                        key=lambda i: int(i['id'])):
                        for i in music.diff:
                            result_set.append(
                                (music['id'], music['ds'][i], i,
                                 str('{:.1f}'.format(music['ds'][i]))))
                    # print(f'[maimai] rs: {result_set}')
                    _while_switch = True
                    turn = 0
                    while _while_switch:
                        turn += 1
                        if (len(result_set) != 0) and turn < 400:
                            _music_dat = result_set.pop(
                                random.randint(0,
                                               len(result_set) - 1))
                            for _achievement in achievement_ls:
                                _music_ra = computeRa(_music_dat[1],
                                                      _achievement)
                                # print(f'[maimai] {_music_ra} > {min_ra}')
                                if (str(_music_dat[0]) +
                                        str(_music_dat[3])) in ate_dict:
                                    if ate_dict[str(_music_dat[0]) +
                                                str(_music_dat[3])] >= 100.5:
                                        break
                                    elif _achievement > ate_dict[
                                            str(_music_dat[0]) +
                                            str(_music_dat[3])]:
                                        if _music_ra > min_ra:
                                            music_ls.append(
                                                (ate_dict[str(_music_dat[0]) +
                                                          str(_music_dat[3])],
                                                 _music_dat[0], _music_dat[2]))
                                            _while_switch = False
                                            break
                                else:
                                    if _music_ra > min_ra:
                                        music_ls.append((-1 * achievement_ls[
                                            achievement_ls.index(_achievement)
                                            - 1], str(_music_dat[0]),
                                                         _music_dat[2]))
                                        _while_switch = False
                                        break
                        else:
                            return (900, None, None)
                else:
                    return (900, None, None)
        if len(music_ls) != 0:
            return random.choice(music_ls)
        else:
            return (900, None, None)
