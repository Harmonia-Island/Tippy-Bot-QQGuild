from botpy import BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message
from models.maimaidx import MaimaiUserData
from models.arcaea import ArcaeaUserData
from service.log import logger
from plugins.arcaea import userInfoByName


@Commands("绑定")
async def bind(api: BotAPI, message: Message, params: str = None):
    commands = params.split()
    if len(commands) != 2:
        await message.reply(content="请在指令后输入需要绑定的游戏和账号\n例如: \"/绑定 舞萌 tippy\"")
        return False
    if commands[0] in ["舞萌", 'maimai']:
        gametype = 'maimai'
    elif commands[0] in ["arc", "arcaea", "Arcaea"]:
        gametype = 'arcaea'
    if commands[1] == 'bottest':
        account = 'tippy'
    else:
        account = commands[1]

    if gametype == 'maimai':
        await MaimaiUserData.add_account(guild_id=message.author.id,
                                         username=account)
    elif gametype == 'arcaea':
        result = await userInfoByName(account)
        if result['status'] != 0:
            await message.reply(content=f'遇到了错误！Code: {result["status"]}')
            return False
        await ArcaeaUserData.bind_account(
            message.author.id, result['content']['account_info']['name'],
            int(result['content']['account_info']['code']))
    await message.reply(content="绑定成功！")
    logger.info(f'用户 {message.author.username} 成功绑定了 {gametype} 查分器')
    return True