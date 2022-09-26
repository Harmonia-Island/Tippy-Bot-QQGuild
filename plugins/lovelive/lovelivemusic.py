import json
from configs.path import TXT_PATH
import random
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

class LoveLiveMusic(Dict):
    musicId: Optional[int] = None
    title: Optional[str] = None
    difficulty: Optional[List[int]] = None
    live_time: Optional[int] = None
    member_tag: Optional[str] = None
    jacket: Optional[int] = None
    bgm: Optional[str] = None
    keyword: Optional[str] = None

    def __getattribute__(self, item):
        if item == 'difficulty':
            self[item].sort()
            return self[item]
        elif item in ['musicId', 'title', 'live_time', 'member_tag', 'jacket', 'bgm', 'keyword']:
            return self[item]
        return super().__getattribute__(item)

class LoveLiveMusicList(List[LoveLiveMusic]):
    def by_id(self, music_id: int) -> Optional[LoveLiveMusic]:
        for music in self:
            if music.musicId == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[LoveLiveMusic]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, seed: Optional[int] = None) -> LoveLiveMusic:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(self,
               *,
               difficulty: Optional[Union[int, List[int], Tuple[int, int]]] = ...,
               title_search: Optional[str] = ...,
               keyword: Optional[str] = ...,
               ):
        new_list = LoveLiveMusicList()
        for music in self:
            music = deepcopy(music)
            if not in_or_equal(difficulty, music.difficulty):
                continue
            if not in_or_equal(keyword, music.keyword):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            new_list.append(music)
        return new_list

with open(TXT_PATH / 'lovelive_meta.json', 'r', encoding="utf8") as f:
    __obj = json.load(f)

total_list: LoveLiveMusicList = LoveLiveMusicList(__obj)
for __i in range(len(total_list)):
    total_list[__i] = LoveLiveMusic(total_list[__i])
