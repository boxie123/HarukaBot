import re

from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot, FriendRequestEvent, GroupRequestEvent

from ..utils import safe_send

friend_req = on_request(priority=5)


@friend_req.handle()
async def friend_agree(bot: Bot, event: FriendRequestEvent):
    if str(event.user_id) in bot.config.superusers:
        await bot.set_friend_add_request(flag=event.flag, approve=True)


group_invite = on_request(priority=5)


@group_invite.handle()
async def group_agree(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == "invite" and str(event.user_id) in bot.config.superusers:
        await bot.set_group_add_request(flag=event.flag, sub_type="invite", approve=True)
    elif event.sub_type == "add" and event.group_id == 1065614825:
        if re.search("艾鸽鸽冲鸭", event.comment):
            await bot.set_group_add_request(flag=event.flag, sub_type="add", approve=True)
        else:
            await safe_send(
                bot_id=bot.self_id,
                send_type="group",
                type_id=970612953,
                message=f"舰长群加群申请提醒：\n申请人QQ号：{event.user_id}\n{event.comment}",
                at=False
            )
    elif event.sub_type == "add" and event.group_id == 1054608979:
        if re.search("宠鸽会", event.comment):
            await bot.set_group_add_request(flag=event.flag, sub_type="add", approve=True)
        else:
            await safe_send(
                bot_id=bot.self_id,
                send_type="group",
                type_id=970612953,
                message=f"饭堂群加群申请提醒：\n申请人QQ号：{event.user_id}\n{event.comment}",
                at=False
            )
