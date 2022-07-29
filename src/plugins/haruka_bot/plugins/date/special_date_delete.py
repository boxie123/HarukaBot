from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.typing import T_State

from ...database import DB as db
from ...utils import permission_check

special_date_delete = on_command("删除特殊日期", rule=to_me(), priority=5)
special_date_delete.__doc__ = """删除特殊日期 name"""

special_date_delete.handle()(permission_check)


@special_date_delete.handle()
async def handle_month(
        state: T_State,
        command_arg: Message = CommandArg(),
):
    special_day = command_arg.extract_plain_text().strip()
    state["name"] = special_day


@special_date_delete.handle()
async def _(state: T_State):
    """手动删除特殊日期"""
    result = await db.delete_special(
        name=state["name"],
    )
    if result:
        await special_date_delete.finish(f"已删除特殊日期\"{state['name']}\"")
    await special_date_delete.finish("特殊日期不存在")
