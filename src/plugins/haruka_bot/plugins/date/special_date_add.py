from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.typing import T_State

from ...database import DB as db
from ...utils import permission_check

special_date_add = on_command("添加特殊日期", rule=to_me(), priority=5)
special_date_add.__doc__ = """添加特殊日期 name month day"""

special_date_add.handle()(permission_check)


@special_date_add.handle()
async def handle_month(
        state: T_State,
        command_arg: Message = CommandArg(),
):
    special_day = command_arg.extract_plain_text().split()
    if special_day[1].isdecimal() and special_day[2].isdecimal():
        state["month"] = special_day[1]
        state["day"] = special_day[2]
        state["name"] = special_day[0]
    else:
        await special_date_add.finish("month 和 day 应为纯阿拉伯数字")


@special_date_add.handle()
async def _(state: T_State):
    """手动添加特殊日期"""
    result = await db.add_special(
        name=state["name"],
        month=state["month"],
        day=state["day"],
    )
    if result:
        await special_date_add.finish(f"已添加特殊日期\"{state['name']}\"")
    await special_date_add.finish("添加特殊日期失败，请联系铂屑")
