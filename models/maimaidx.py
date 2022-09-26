from typing import List, Optional

from service.db_context import db


class MaimaiUserData(db.Model):
    __tablename__ = 'maimai_userdata'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String, nullable=False, index=True, unique=True)
    username = db.Column(db.String, nullable=False)
    plate = db.Column(db.Integer)
    icon = db.Column(db.Integer)
    title = db.Column(db.Integer)
    frame = db.Column(db.Integer)

    @classmethod
    async def add_account(cls,
                          guild_id: str,
                          username: str,
                          plate: Optional[int] = None,
                          icon: Optional[int] = None,
                          title: Optional[int] = None,
                          frame: Optional[int] = None) -> bool:
        """
        说明：
            添加账号
        参数：
            :param username: 账号
            :param plate: 姓名框
            :param icon: 头像
            :param title: 标题
            :param frame: 底板
        """
        query = cls.query.where(cls.guild_id == guild_id)
        group = await query.gino.first()
        if not group:
            await cls.create(guild_id=guild_id,
                             username=username,
                             plate=plate,
                             icon=icon,
                             frame=frame,
                             title=title)
            return True
        else:
            if plate:
                update = await group.update(guild_id=guild_id,
                                            username=username,
                                            plate=plate).apply()
            if icon:
                update = await group.update(guild_id=guild_id,
                                            username=username,
                                            icon=icon).apply()
            if frame:
                update = await group.update(guild_id=guild_id,
                                            username=username,
                                            frame=frame).apply()
            if title:
                update = await group.update(guild_id=guild_id,
                                            username=username,
                                            title=title).apply()
            if update:
                return True
        return False

    @classmethod
    async def get_info(cls,
                       username: Optional[str] = None,
                       guild_id: Optional[str] = None):
        """
        说明：
            获取账号信息
        参数：
            :param username: 账号
        """
        if username is not None:
            query = cls.query.where(cls.username == username)
        elif guild_id is not None:
            query = cls.query.where(cls.guild_id == guild_id)
        else:
            return False
        group = await query.gino.first()
        if group:
            return group
        else:
            return None

    @classmethod
    async def delete_account(cls, guild_id: str) -> bool:
        """
        说明：
            删除账号
        参数：
            :param username: 账号
        """
        query = cls.query.where(cls.guild_id == guild_id).with_for_update()
        user = await query.gino.first()
        if not user:
            return False
        await cls.delete.where(cls.guild_id == guild_id).gino.status()
        return True