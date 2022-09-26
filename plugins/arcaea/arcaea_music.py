import os
import random
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Union

from configs.path import VOICE_PATH
from .BotArcAPI import getDB


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis or checker is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


class ArcaeaMusic(Dict):
    musicId: Optional[int] = None
    songId: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    difficulty: Optional[List[int]] = None
    bpm: Optional[str] = None
    package: Optional[str] = None
    version: Optional[str] = None
    date: Optional[int] = None
    hasAudio: Optional[bool] = None

    def __getattribute__(self, item):
        if item in self:
            return self[item]
        return super().__getattribute__(item)


class ArcaeaMusicList(List[ArcaeaMusic]):

    def by_id(self, music_id: int) -> Optional[ArcaeaMusic]:
        for music in self:
            if music.musicId == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[ArcaeaMusic]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, seed: Optional[int] = None) -> ArcaeaMusic:
        if seed is not None:
            random.seed(seed)
        return random.choice(self)

    def filter(
        self,
        *,
        difficulty: Optional[Union[int, List[int], Tuple[int, int], str,
                                   List[str]]] = ...,
        title_search: Optional[str] = ...,
    ):
        new_list = ArcaeaMusicList()
        for music in self:
            music = deepcopy(music)
            if not in_or_equal(difficulty, music.difficulty):
                continue
            if title_search is not Ellipsis and title_search.lower(
            ) not in music.title.lower():
                continue
            new_list.append(music)
        return new_list


__arcsongdb = getDB()
__adbp_cur = __arcsongdb.cursor()
__adbp_cur.execute('SELECT DISTINCT "id", "name" FROM packages')
__arc_packages = {x: y for x, y in __adbp_cur}

__adbs_cur = __arcsongdb.cursor()
__adbs_cur.execute(
    'SELECT DISTINCT "song_id", "name_en", "name_jp", "artist", "bpm", "set", "date", "version", "difficulty" FROM charts'
)
__arc_songs_d = {}
__arc_songs_l = []
for entry in __adbs_cur:
    if entry[0] not in __arc_songs_d:
        __arc_songs_d[entry[0]] = {
            'songId':
            entry[0],
            'title':
            entry[2] if entry[2] else entry[1],
            'artist':
            entry[3],
            'bpm':
            entry[4],
            'package':
            __arc_packages[entry[5]],
            'date':
            entry[6],
            'version':
            entry[7],
            'difficulty': [entry[8]],
            'hasAudio':
            os.path.exists(VOICE_PATH / 'arcaea' / 'bgm' / f"{entry[0]}.mp3")
        }
    else:
        __arc_songs_d[entry[0]]['difficulty'].append(entry[8])

for idx, entry in enumerate(list(__arc_songs_d.values())):
    e = dict(entry)
    e['musicId'] = idx
    e['difficulty'].sort()
    __arc_songs_l.append(e)

total_list: ArcaeaMusicList = ArcaeaMusicList(__arc_songs_l)
for __i in range(len(total_list)):
    total_list[__i] = ArcaeaMusic(total_list[__i])

del __arc_songs_d
del __arc_songs_l
