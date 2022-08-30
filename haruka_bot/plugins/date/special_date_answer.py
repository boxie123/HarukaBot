import traceback

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.typing import T_State

from ...utils import get_special_date

special_date_answer = on_command("查询节假日", aliases={"获取节假日"}, rule=to_me(), priority=5)
special_date_answer.__doc__ = """查询节假日"""


@special_date_answer.handle()
async def handle_month(
    state: T_State,
    command_arg: Message = CommandArg(),
):
    month = command_arg.extract_plain_text().strip()
    if month.isdecimal():
        state["month"] = month


@special_date_answer.handle()
async def _(state: T_State):
    message = "获取节假日失败，请联系铂屑"
    try:
        if "month" in state:
            message = await get_special_date(is_week=False, month=state["month"])
        else:
            message = await get_special_date(is_week=False)
    except Exception:
        logger.error("获取节假日信息失败，以下为错误日志：")
        logger.error(traceback.format_exc())
    await special_date_answer.finish(message)
