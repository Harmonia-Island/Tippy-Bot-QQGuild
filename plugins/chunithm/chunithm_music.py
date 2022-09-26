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
    note: Optional[list] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'note':
            return self['notes']
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)


class ChuniMusic(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    cue: Optional[dict] = None
    bpm: Optional[int] = None
    jacket: Optional[str] = None
    version: Optional[str] = None
    charts: Optional[Chart] = None

    release_date: Optional[str] = None
    artist: Optional[str] = None

    def __getattribute__(self, item):
        if item in {
                'genre', 'artist', 'release_date', 'bpm', 'version', 'jacket',
                'cue'
        }:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class ChuniMusicList(List[ChuniMusic]):
    def by_id(self, music_id: str) -> Optional[ChuniMusic]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[ChuniMusic]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, seed: Optional[str] = None) -> Optional[ChuniMusic]:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(
        self,
        *,
        title_search: Optional[str] = ...,
        genre: Optional[Union[str, List[str]]] = ...,
        version: Optional[Union[str, List[str]]] = ...,
    ) -> Optional["ChuniMusicList"]:
        new_list = ChuniMusicList()
        for music in self:
            music = deepcopy(music)
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.version, version):
                continue
            if title_search is not Ellipsis and title_search.lower(
            ) not in music.title.lower():
                continue
            new_list.append(music)
        return new_list


chuni_music_list: ChuniMusicList = ChuniMusicList(
    json.load(
        open(TXT_PATH / 'chunithm' / 'chunimusic_new.json',
             'r',
             encoding="utf8")))
for __i in range(len(chuni_music_list)):
    chuni_music_list[__i] = ChuniMusic(chuni_music_list[__i])
    for __j in range(len(chuni_music_list[__i].charts)):
        if chuni_music_list[__i].charts[__j] is None:
            continue
        chuni_music_list[__i].charts[__j] = Chart(
            chuni_music_list[__i].charts[__j])

chuniversion = {
    '0': 'Chunithm',
    '1': 'Chunithm PLUS',
    '2': 'Chunithm AIR',
    '3': 'Chunithm AIR PLUS',
    '4': 'Chunithm STAR',
    '5': 'Chunithm STAR PLUS',
    '6': 'Chunithm AMAZON',
    '7': 'Chunithm AMAZON PLUS',
    '8': 'Chunithm CRYSTAL',
    '9': 'Chunithm CRYSTAL PLUS',
    '10': 'Chunithm PARADISE',
    '11': 'Chunithm PARADISE LOST',
    '12': 'Chunithm NEW!!',
    '13': 'Chunithm NEW PLUS!!',
}

chu_we_diff = {
    "11": "招",
    "12": "狂",
    "13": "止",
    "14": "改",
    "15": "両",
    "16": "嘘",
    "17": "半",
    "18": "時",
    "19": "光",
    "110": "割",
    "112": "弾",
    "113": "戻",
    "115": "布",
    "116": "敷",
    "119": "？",
    "120": "！",
    "121": "避",
    "122": "速",
    "123": "歌",
    "124": "撃",
    "125": "舞",
    "127": "蔵",
    "128": "覚"
}