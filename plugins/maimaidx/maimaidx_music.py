import json
import os
import random
from typing import Dict, List, Literal, Optional, Union, Tuple, Any
from copy import deepcopy

from configs.path import TXT_PATH


def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    if type(checker[0]) != type(checker[-1]):
        print('Detected different data types')
        checker = [x for x in checker if not isinstance(x, str)]
    # print(checker, elem, diff)
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        # print(elem)
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self['notes'][0]
        elif item == 'hold':
            return self['notes'][1]
        elif item == 'slide':
            return self['notes'][2]
        elif item == 'touch':
            return self['notes'][3] if len(self['notes']) == 5 else 0
        elif item == 'brk':
            return self['notes'][-1]
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)


class Stats(Dict):
    count: Optional[int] = None
    avg: Optional[float] = None
    sss_count: Optional[int] = None
    difficulty: Optional[str] = None
    rank: Optional[int] = None
    total: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'sss_count':
            return self['sssp_count']
        elif item == 'rank':
            return self['v'] + 1
        elif item == 'total':
            return self['t']
        elif item == 'difficulty':
            return self['tag']
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class MaiMusic(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Literal["SD", "DX"] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    charts: Optional[Chart] = None
    stats: Optional[List[Stats]] = None

    release_date: Optional[str] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version'}:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class MaiMusicList(List[MaiMusic]):
    def by_id(self, music_id: str) -> Optional[MaiMusic]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[MaiMusic]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, seed: Optional[str] = None) -> Optional[MaiMusic]:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(
        self,
        *,
        level: Optional[Union[str, List[str]]] = ...,
        ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
        title_search: Optional[str] = ...,
        genre: Optional[Union[str, List[str]]] = ...,
        bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
        type: Optional[Union[str, List[str]]] = ...,
        diff: List[int] = ...,
        version: Optional[Union[str, List[str]]] = ...,
    ) -> Optional["MaiMusicList"]:
        new_list = MaiMusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue

            # print(f'music.ds:{music.ds}, ds:{ds}, diff2:{diff2}')
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if not in_or_equal(music.version, version):
                continue
            if title_search is not Ellipsis and title_search.lower(
            ) not in music.title.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list


# 舞萌DX2021
stats = json.load(
    open(TXT_PATH / 'maimai' / 'maimaimusic_stats.json', 'r',
         encoding="utf8")) if os.path.exists(TXT_PATH / 'maimai' /
                                             'maimaimusic_stats.json') else {}
total_list: MaiMusicList = MaiMusicList(
    json.load(
        open(TXT_PATH / 'maimai' / 'maimaimusic.json', 'r', encoding="utf8")))
for __i in range(len(total_list)):
    total_list[__i] = MaiMusic(total_list[__i])
    if stats != {}:
        total_list[__i]['stats'] = stats[total_list[__i].id]
    for __j in range(len(total_list[__i].charts)):
        total_list[__i].charts[__j] = Chart(total_list[__i].charts[__j])
        if stats != {}:
            total_list[__i].stats[__j] = Stats(total_list[__i].stats[__j])

# maimai DX UNiVERSE                                                                                  'maimaimusic_stats.json') else {}
total_list_jp: MaiMusicList = MaiMusicList(
    json.load(
        open(TXT_PATH / 'maimai' / 'maimusic_universe.json',
             'r',
             encoding="utf8")))
for __i in range(len(total_list_jp)):
    total_list_jp[__i] = MaiMusic(total_list_jp[__i])
    for __j in range(len(total_list_jp[__i].charts)):
        total_list_jp[__i].charts[__j] = Chart(total_list_jp[__i].charts[__j])

all_plate_id = {
    "真極": 6101,
    "真舞舞": 6103,
    "真神": 6102,
    "超極": 6104,
    "超将": 6105,
    "超舞舞": 6107,
    "超神": 6106,
    "檄極": 6108,
    "檄将": 6109,
    "檄舞舞": 6111,
    "檄神": 6110,
    "橙極": 6112,
    "橙将": 6113,
    "橙舞舞": 6115,
    "橙神": 6114,
    "暁極": 6116,
    "暁将": 6117,
    "暁舞舞": 6119,
    "暁神": 6118,
    "桃極": 6120,
    "桃将": 6121,
    "桃舞舞": 6123,
    "桃神": 6122,
    "櫻極": 6124,
    "櫻将": 6125,
    "櫻舞舞": 6127,
    "櫻神": 6126,
    "紫極": 6128,
    "紫将": 6129,
    "紫舞舞": 6131,
    "紫神": 6130,
    "菫極": 6132,
    "菫将": 6133,
    "菫舞舞": 6135,
    "菫神": 6134,
    "白極": 6136,
    "白将": 6137,
    "白舞舞": 6139,
    "白神": 6138,
    "雪極": 6140,
    "雪将": 6141,
    "雪舞舞": 6143,
    "雪神": 6142,
    "輝極": 6144,
    "輝将": 6145,
    "輝舞舞": 6147,
    "輝神": 6146,
    "霸者": 6148,
    "熊極": 55101,
    "熊将": 55102,
    "熊舞舞": 55104,
    "熊神": 55103,
    "華極": 109101,
    "華将": 109102,
    "華舞舞": 109104,
    "華神": 109103,
    "爽極": 159101,
    "爽将": 159102,
    "爽舞舞": 159104,
    "爽神": 159103,
    "舞極": 6149,
    "舞将": 6150,
    "舞舞舞": 6152,
    "舞神": 6151,
    "kop19FL": 50002,
    "kop19T1": 50001,
    "kop20FL": 100003,
    "kop20T1": 100001,
    "kop20SC": 100004,
}

maimai_versions = {
    "maimai": '100',
    "maimai PLUS": '110',
    "maimai GreeN": '120',
    "maimai GreeN PLUS": '130',
    "maimai ORANGE": '140',
    "maimai ORANGE PLUS": '150',
    "maimai PiNK": '160',
    "maimai PiNK PLUS": '170',
    "maimai MURASAKi": '180',
    "maimai MURASAKi PLUS": '185',
    "maimai MiLK": '190',
    "maimai MiLK PLUS": '195',
    "MiLK PLUS": '195',
    "maimai FiNALE": '199',
    "maimai DX": '200',
    "maimai DX PLUS": '210',
    "maimai DX Splash": '214',
    "maimai DX Splash PLUS": '215',
    "maimai DX UNiVERSE": '220',
    "maimai DX UNiVERSE PLUS": '225',
    "maimai \u3067\u3089\u3063\u304f\u3059": 'CN200',
    "maimai \u3067\u3089\u3063\u304f\u3059 Splash": 'CN210',
    "maimai \u3067\u3089\u3063\u304f\u3059 Splash PLUS": 'CN220',
}

maiversion = {
    '0': 'maimai',
    '1': 'maimai PLUS',
    '2': 'maimai GreeN',
    '3': 'maimai GreeN PLUS',
    '4': 'maimai ORANGE',
    '5': 'maimai ORANGE PLUS',
    '6': 'maimai PiNK',
    '7': 'maimai PiNK PLUS',
    '8': 'maimai MURASAKi',
    '9': 'maimai MURASAKi PLUS',
    '10': 'maimai MiLK',
    '11': 'maimai MiLK PLUS',
    '12': 'maimai FiNALE',
    '13': 'maimai DX',
    '14': 'maimai DX PLUS',
    '15': 'maimai DX Splash',
    '16': 'maimai DX Splash PLUS',
    '17': 'maimai DX UNiVERSE',
    '18': 'maimai DX UNiVERSE PLUS',
}

mai_region = {'SDEZ': 'DX', 'SDGA': 'EX', 'SDGB': 'CH'}
