from ...utils import safe_send, scheduler, getInfo


@scheduler.scheduled_job(
    # "cron", day_of_week=0, hour=0, minute=random.randint(0, 10), second=0, id="special_date_sched",
    "cron", day_of_week=4, hour=13, minute=43, second=0, id="special_date_sched",
)
async def sd_sched():
    message_str = await getInfo()
    push_list = [
        {"type": "private", "type_id": 1824390830},
        # {"type": "private", "type_id": 137353452},
        # {"type": "group", "type_id": 970612953},
    ]
    for push in push_list:
        await safe_send(
            # bot_id=3283903771,
            bot_id=1031515006,
            send_type=push["type"],
            type_id=push["type_id"],
            message=message_str,
            at=False,
        )

