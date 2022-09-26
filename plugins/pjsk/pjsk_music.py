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


class SekaiMusic(Dict):
    musicId: Optional[int] = None
    title: Optional[str] = None

    difficulty: Optional[List[int]] = None
    publishedAt: Optional[str] = None
    composer: Optional[str] = None
    lyricist: Optional[str] = None
    arranger: Optional[str] = None
    vocals: Optional[List[str]] = None
    characters: Optional[List[list]] = None
    categories: Optional[List[str]] = None

    def __getattribute__(self, item):
        if item == 'difficulty':
            if item in self:
                self[item].sort()
                return self[item]
            else:
                return [0, 0, 0, 0, 0]
        elif item in {
                'musicId', 'title', 'publishedAt', 'composer', 'lyricist',
                'arranger', 'vocals', 'characters', 'categories'
        }:
            return self[item]
        return super().__getattribute__(item)


class SekaiMusicList(List[SekaiMusic]):
    def by_id(self, music_id: int) -> Optional[SekaiMusic]:
        for music in self:
            if music.musicId == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[SekaiMusic]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, seed: Optional[int] = None) -> SekaiMusic:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(
        self,
        *,
        difficulty: Optional[Union[int, List[int], Tuple[int, int]]] = ...,
        title_search: Optional[str] = ...,
        composer: Optional[str] = ...,
        arranger: Optional[str] = ...,
        lyricist: Optional[str] = ...,
    ):
        new_list = SekaiMusicList()
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
            if title_search is not Ellipsis and title_search.lower(
            ) not in music.title.lower():
                continue
            new_list.append(music)
        return new_list


with open(TXT_PATH / 'pjsk' / 'pjsk_music.json', 'r', encoding="utf8") as f:
    __obj = json.load(f)

total_list: SekaiMusicList = SekaiMusicList(__obj)
for __i in range(len(total_list)):
    total_list[__i] = SekaiMusic(total_list[__i])
