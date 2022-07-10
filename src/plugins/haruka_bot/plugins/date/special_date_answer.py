import traceback

from nonebot import on_command
from nonebot.log import logger
from nonebot.rule import to_me

from ...utils import dateReminder

special_date_answer = on_command("查询节假日", rule=to_me(), priority=5)
special_date_answer.__doc__ = """查询节假日"""


# TODO 可自定义查询月份
@special_date_answer.handle()
async def _():
    message = "获取节假日失败，请联系铂屑"
    try:
        data_item = dateReminder(is_week=False)
        message = await data_item.outputStr()
    except Exception:
        logger.error("获取节假日信息失败，以下为错误日志：")
        logger.error(traceback.format_exc())
        await special_date_answer.finish(message)
    await special_date_answer.finish("本月节假日为：\n" + message)
