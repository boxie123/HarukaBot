import asyncio
from httpx import AsyncClient
import datetime
import random


# 随机获取一个认证头
def get_user_agents():
    agent = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
    ]
    return random.choice(agent)


# 当用户按月查询的时候，会建立importantDate实例，用来储存一个每个重要日子的
#   名字，是否放假，节日日期和调休工作日属性。若用户按周查询，不会使用该class
class importantDate:
    # 构造函数
    def __init__(self, name, do_rest, first_date):
        self.name = name
        self.do_rest = do_rest
        self.holidays = [first_date]
        self.workdays = []
    
    # 转str函数，可直接获得整理好的结果
    # 示例：
    #   #劳动节
    #   放假日期：1号，2号，3号，4号
    #   调休工作日：7号
    #
    #   #汶川大地震纪念日
    #   本节日不放假，日期：12号
    #   调休工作日：无
    def __str__(self):
        output = "#{}\n".format(self.name)
        if (not self.do_rest):
            output += "本节日不放假，日期："
        else:
            output += "放假日期："
        
        for date in self.holidays:
            output += "{}号，".format(str(date))
        output = output[:-1] + "\n"
        
        output += "调休工作日："
        if len(self.workdays) != 0:
            for date in self.workdays:
                output += "{}号，".format(str(date))
            output = output[:-1] + "\n"
        else:
            output += "无\n"
            
        return output


# 本模块核心class，创建实例时需要传入is_week，True表示按周查询，False表示按月查询。
# 示例：
#   item = dateReminder(is_week=True)   创建实例，按周查询
#   print(item.outputStr())             获取查询结果str
class dateReminder:
    def __init__(self, is_week):
        # 查询时的日期
        self.today = datetime.date.today()

        # 是否按周查询
        self.is_week = is_week

        # special_dates包含了日历api无法查到的特殊日子，格式是{月份(int): importantDate}
        #   需要手动更新
        self.special_dates = {
            5: [importantDate("汶川大地震纪念日", False, 12)],
            6: [importantDate("服务器维护", False, 4)],
            7: [importantDate("七七事变", False, 7)],
            9: [importantDate("抗日战争胜利纪念日", False, 3),
                importantDate("九一八事变", False, 18),
                importantDate("烈士纪念日", False, 30)],
            12: [importantDate("南京大屠杀纪念日", False, 13)]
        }
        
        # 如果是按周查询，则result是{星期数(int)：”节日名，放假/不放假/调休“}
        # 如果是按月查询，则result是{“节日名”：importantDate}
        self.result = {}


    # 获取放假及调休信息（更新self.result并返回）
    async def getInfo(self):
        async def getRawResp(client, is_holiday, is_week):
            url = "https://api.apihubs.cn/holiday/get"
            headers = {
                "User-Agent": get_user_agents(),
                "Referer": "https://www.baidu.com/"
            }
            rest_params = {
                "order_by": 1,
                "holiday" if is_holiday else "holiday_overtime": 99,
                "cn": 1,
                "size": 31
            }
            if is_week:
                rest_params["yearweek"] = self.today.strftime("%Y%W")
            else:
                rest_params["month"] = self.today.strftime("%Y%m")

            resp = await client.request(method="get", url=url, params=rest_params, headers=headers)
            resp.encoding = "utf-8"
            rest_info = resp.json()
            if rest_info["code"] != 0:
                raise Exception("日期api获取错误，请联系开发者")

            return resp.json()
        
        # 从api获取raw reponse信息
        async with AsyncClient() as client:
            is_holiday = True 
            rest_info = await getRawResp(client, is_holiday, self.is_week)
            work_info = await getRawResp(client, (not is_holiday), self.is_week)
        
        raw_holidays_info = rest_info["data"]["list"]
        raw_workday_info = work_info["data"]["list"]

        # 获取放假信息
        for day in raw_holidays_info:
            name = day["holiday_cn"]
            date = day["date"] % 100
            week = day["week"]
            rest = (day["holiday_recess_cn"] == "假期节假日")
            if (self.is_week):
                self.result[week] = "{}，{}".format(name, ("放假" if rest else "不放假"))                
            else:
                if not name in self.result:
                    self.result[name] = importantDate(name, rest, date)
                else:
                    self.result[name].holidays.append(date)

        # 获取调休信息
        for day in raw_workday_info:
            name = day["holiday_overtime_cn"][:-2]
            week = day["week"]
            date = day["date"] % 100
            if (self.is_week):
                self.result[week] = "{}调休".format(name)
            else:
                # 如果有调休，那这个name一定是节假日且一定在result中
                self.result[name].workdays.append(date)

        # 加入特殊日期
        for month in self.special_dates:
            for day in self.special_dates[month]:
                if (self.is_week):
                    start = self.today - datetime.timedelta(self.today.weekday())       # 本周周一日期
                    end = start + datetime.timedelta(7)                                 # 本周周日日期
                    format_day = datetime.date(self.today.year, month, day.holidays[0])
                    if (format_day >= start and format_day <= end):                     # 查看day是否在本周期间
                        week = format_day.weekday() + 1                                 # +1因为monday为0
                        self.result[week] = "{}，{}".format(day.name, ("放假" if day.do_rest else "不放假"))
                else:
                    if (self.today.month == month):
                        self.result[day.name] = day
 
        return self.result


    # 将self.result用文本格式化后输出str
    async def outputStr(self):
        await self.getInfo()
        output = ""

        if (self.is_week): 
            if (len(self.result) == 0): return "本周无重要日期\n"
            week_num_to_str = {
                1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"
            } 
            monday = self.today - datetime.timedelta(self.today.weekday())
            output = "本周（从{}月{}号周一开始）重要日期提醒:\n".format(monday.month, monday.day)
            for week in self.result:
                output += "{}：{}\n".format(week_num_to_str[week], self.result[week])
        else: 
            if (len(self.result) == 0): return "本月无重要日期\n"
            for day in self.result:
                output += (str(self.result[day]) + '\n')

        return output


