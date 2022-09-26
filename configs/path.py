from pathlib import Path

_TIPPY_PATH = Path("")
LOG_PATH = _TIPPY_PATH / Path("log/")
DATA_PATH = _TIPPY_PATH / Path("data/")
TXT_PATH = _TIPPY_PATH / Path('resources/text/')
FONT_PATH = _TIPPY_PATH / Path("resources/font/")
IMAGE_PATH = _TIPPY_PATH / Path("resources/img/")
VOICE_PATH = _TIPPY_PATH / Path("resources/voice/")
RESOURCE_PATH = _TIPPY_PATH / Path("resources/")
TEMP_PATH = Path("temp/")
if not TEMP_PATH.exists():
    TEMP_PATH.mkdir()
