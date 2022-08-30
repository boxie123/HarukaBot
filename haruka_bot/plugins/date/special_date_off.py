from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent

from ...database import DB as db
from ...utils import get_type_id, permission_check, to_me

special_date_off = on_command("关闭节假日提醒", rule=to_me(), priority=5)
special_date_off.__doc__ = """关闭节假日提醒"""

special_date_off.handle()(permission_check)


@special_date_off.handle()
async def _(event: MessageEvent):
    """删除节假日提醒订阅"""
    result = await db.delete_date(
        type=event.message_type, type_id=get_type_id(event)
    )
    if result:
        await special_date_off.finish("已关闭节假日订阅")
    await special_date_off.finish("节假日订阅未开启")
