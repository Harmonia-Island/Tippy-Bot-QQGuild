import json
from configs.path import TXT_PATH
import random
import time
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy

def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis or checker is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem



class GBPMusic(Dict):
    musicId: Optional[int] = None
    musicTitle: Optional[str] = None
    bandName: Optional[str] = None
    bandId: Optional[int] = None
    jacket: Optional[str] = None
    bgmId: Optional[str] = None
    difficulty: Optional[List[int]] = None
    publishedAt: Optional[str] = None
    composer: Optional[str] = None
    lyricist: Optional[str] = None
    arranger: Optional[str] = None
    howToGet: Optional[str] = None

    def __getattribute__(self, item):
        if item == 'jacket':
            return self[item][1:].replace('webp', 'png')
        elif item == 'difficulty':
            self[item].sort()
            return self[item]
        elif item in {'musicId', 'musicTitle', 'publishedAt', 'composer', 'lyricist', 'arranger', 'howToGet', 'bandId', 'bandName', 'bgmId'}:
            return self[item]
        return super().__getattribute__(item)


class GBPMusicList(List[GBPMusic]):
    def by_id(self, music_id: int) -> Optional[GBPMusic]:
        for music in self:
            if music.musicId == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[GBPMusic]:
        for music in self:
            if music.musicTitle == music_title:
                return music
        return None

    def random(self, seed: Optional[int] = None) -> GBPMusic:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(self,
               *,
               difficulty: Optional[Union[int, List[int], Tuple[int, int]]] = ...,
               title_search: Optional[str] = ...,
               year_search: Optional[int] = ...,
               composer: Optional[str] = ...,
               arranger: Optional[str] = ...,
               lyricist: Optional[str] = ...,
               bandName: Optional[str] = ...,
               ):
        new_list = GBPMusicList()
        for music in self:
            music = deepcopy(music)
            if not in_or_equal(difficulty, music.difficulty):
                continue
            if not in_or_equal(music.composer, composer):
                continue
            if not in_or_equal(music.arranger, arranger):
                continue
            if not in_or_equal(music.lyricist, lyricist):
                continue
            if not in_or_equal(music.bandName, bandName):
                continue
            if not in_or_equal(time.localtime(int(music.publishedAt[:-3])).tm_year, year_search):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.musicTitle.lower():
                continue
            new_list.append(music)
        return new_list

with open(TXT_PATH / 'bang_dream_meta.json', 'r', encoding="utf8") as f:
    __obj = json.load(f)

total_list: GBPMusicList = GBPMusicList(__obj['data'])
for __i in range(len(total_list)):
    total_list[__i] = GBPMusic(total_list[__i])

