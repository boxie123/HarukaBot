import traceback

from ...database import DB as db
from ...utils import safe_send, scheduler, dateReminder

from nonebot.log import logger


async def sd_sched(is_week: bool = True):
    message = "获取节假日失败，请联系铂屑"
    try:
        data_item = dateReminder(is_week=is_week)
        message = await data_item.outputStr()
    except Exception:
        logger.error("获取节假日信息失败，以下为错误日志：")
        logger.error(traceback.format_exc())

    push_list = await db.get_date_list()
    for sets in push_list:
        logger.info("定时任务 special_date_sched 执行，发送消息给{}".format(sets.type_id))
        await safe_send(
            bot_id=sets.bot_id,
            send_type=sets.type,
            type_id=sets.type_id,
            message="定时温馨提醒：\n" + message,
            at=False
        )
    for push in push_list:
        logger.info("定时任务 special_date_sched 执行，发送消息给{}".format(push["type_id"]))
        await safe_send(
            bot_id=3283903771,
            # bot_id=1031515006,
            send_type=push["type"],
            type_id=push["type_id"],
            message="定时温馨提醒：\n" + message,
            at=False,
        )

scheduler.add_job(
    sd_sched, "cron", args=(True,), day_of_week=0, hour=0, minute=3, second=0, id="special_date_sched_week",
    # sd_sched, "cron", args=(True,), day_of_week=5, hour=16, minute=8, second=30, id="special_date_sched_week",
)
scheduler.add_job(
    sd_sched, "cron", args=(False,), day=1, hour=0, minute=3, second=0, id="special_date_sched_month",
    # sd_sched, "cron", args=(False,), day_of_week=5, hour=16, minute=9, second=0, id="special_date_sched_month",
)
