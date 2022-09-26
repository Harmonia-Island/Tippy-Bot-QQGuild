from typing import List, Optional

from service.db_context import db


class ArcaeaUserData(db.Model):
    __tablename__ = 'arcaea_userdata'
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String, nullable=False, index=True, unique=True)
    username = db.Column(db.String, nullable=False)
    usercode = db.Column(db.Integer, nullable=False)

    @classmethod
    async def bind_account(cls, qq: str, username: str, usercode: int) -> bool:
        """
        说明：
            绑定账号
        参数：
            :param username: 账号
            :param usercode: code
        """
        query = cls.query.where(cls.qq == qq)
        group = await query.gino.first()
        if not group:
            await cls.create(qq=qq, username=username, usercode=usercode)
            return True
        else:
            if usercode and username:
                update = await group.update(qq=qq,
                                            username=username,
                                            usercode=usercode).apply()
            if update:
                return True
        return False

    @classmethod
    async def get_bind(cls, qq: str) -> Optional["ArcaeaUserData"]:
        """
        说明：
            获取账号信息
        参数：
            :param qq: 账号
        """
        query = cls.query.where(cls.qq == qq)
        group = await query.gino.first()
        if group:
            return group
        else:
            return None

    @classmethod
    async def unbind_account(cls, qq: str) -> bool:
        """
        说明：
            删除账号
        参数：
            :param qq: 账号
        """
        query = cls.query.where(cls.qq == qq).with_for_update()
        user = await query.gino.first()
        if not user:
            return False
        await cls.delete.where(cls.qq == qq).gino.status()
        return True