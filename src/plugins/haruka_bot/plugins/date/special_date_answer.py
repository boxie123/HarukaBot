from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State

from ...utils import getInfo

special_date_answer = on_command("查询节假日", rule=to_me(), priority=5)
special_date_answer.__doc__ = """查询节假日"""


@special_date_answer.handle()
async def _(event: MessageEvent, state: T_State):
    message_str = await getInfo(False)
    await special_date_answer.finish("本月节假日为：\n" + message_str)
