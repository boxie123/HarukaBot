import traceback

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State
from nonebot.log import logger

from ...utils import dateReminder

special_date_answer = on_command("查询节假日", rule=to_me(), priority=5)
special_date_answer.__doc__ = """查询节假日"""


@special_date_answer.handle()
async def _(event: MessageEvent, state: T_State):
    message_str = "获取节假日失败，请联系铂屑"
    try:
        data_item = dateReminder(is_week=False)
        message_str = await data_item.outputStr()
    except Exception:
        logger.error("获取节假日信息失败，以下为错误日志：")
        logger.error(traceback.format_exc())
        await special_date_answer.finish(message_str)
    await special_date_answer.finish("本月节假日为：\n" + message_str)
