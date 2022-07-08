import random
import traceback
from httpx import AsyncClient
import datetime

from nonebot.log import logger


# 随机获取一个认证头
def get_user_agents():
    agent = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
    ]
    return random.choice(agent)


headers = {
    "User-Agent": get_user_agents(),
    "Referer": "https://www.baidu.com/"
}


async def get_raw_resp(client: AsyncClient, is_holiday: bool = True, is_week: bool = True):
    today = datetime.date.today()
    url = "https://api.apihubs.cn/holiday/get"
    rest_params = {
        "order_by": 1,
        "holiday" if is_holiday else "holiday_overtime": 99,
        "cn": 1,
        "size": 31
    }
    if is_week:
        rest_params["yearweek"] = today.strftime("%Y%W")
    else:
        rest_params["month"] = today.strftime("%Y%m")
    resp = await client.request(method="get", url=url, params=rest_params, headers=headers)
    resp.encoding = "utf-8"

    return resp.json()


def getHoliday(rest_info, result):
    assert rest_info["code"] == 0
    holidays = rest_info["data"]["list"]

    for day in holidays:
        name = day["holiday_cn"]
        else_holiday = day["holiday_or_cn"]
        if else_holiday != name:
            name = ",".join((name, else_holiday))
        date = day["date_cn"]
        rest = day["holiday_recess_cn"]
        if name not in result:
            if rest == "假期节假日":
                result[name] = {"放假日期：": [date]}
            else:
                result[name] = {"本节日不放假，日期：": [date]}
        else:
            result[name]["放假日期："].append(date)


def getWorkday(work_info, result):
    assert work_info["code"] == 0
    workdays = work_info["data"]["list"]

    for day in workdays:
        name = day["holiday_overtime_cn"][:-2]
        date = day["date_cn"]
        if "调休工作日：" not in result[name]:
            result[name]["调休工作日："] = [date]
        else:
            result[name]["调休工作日："].append(date)


async def getInfo(is_week: bool = True):
    result = {}
    today = datetime.date.today()
    async with AsyncClient() as client:
        try:
            getHoliday(await get_raw_resp(client, is_week=is_week), result)
            getWorkday(await get_raw_resp(client, is_holiday=False, is_week=is_week), result)
        except Exception:
            logger.error("获取节假日失败，请查看错误日志：")
            logger.error(traceback.format_exc())
    message1 = printOut(result)
    message2 = printImportantDay(today.month)
    message1.extend(message2)
    message_str = "".join(message1)
    return message_str


def printOut(result):
    today = datetime.date.today()
    message_list = ["{}月和{}月的节日放假调休信息:\n".format(today.month, today.month + 1)]
    for holiday in result:
        message_list.append("=" * 15 + holiday + "=" * 15 + "\n")
        if "放假日期：" in result[holiday]:
            message_list.append("放假日期：\n")
            for date in result[holiday]["放假日期："]:
                message_list.append(date + "  ")
            message_list.append("\n")
            if "调休工作日：" in result[holiday]:
                message_list.append("调休工作日：\n")
                for date in result[holiday]["调休工作日："]:
                    message_list.append(date + "  ")
                message_list.append("\n")
            else:
                message_list.append("本节日无调休\n")
        else:
            message_list.append("本节日不放假，日期：" + result[holiday]["本节日不放假，日期："][0] + "\n")
        message_list.append("\n")
    return message_list


def printImportantDay(curr_month):
    today = datetime.date.today()
    year = str(today.year)
    important_day = {
        5: [year + "年5月12日(汶川大地震纪念)"],
        7: [year + "年7月7日(卢沟桥事变)"],
        9: [year + "年9月3日(抗日战争胜利纪念日)", year + "年9月18日(九一八事变)", year + "年9月30日(烈士纪念日)"],
        12: [year + "年12月13日(南京大屠杀)"]
    }
    message_list = ["\n==========其他重要日子(如纪念日)==========\n"]
    for month in (curr_month, curr_month + 1):
        if month in important_day:
            message_list.append(str(month) + "月：\n")
            for date in important_day[month]:
                message_list.append(date + "\n")
            message_list.append("\n")
    return message_list
