from asyncio import get_running_loop
from random import randint

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot import get_driver, get_bot, on_command, require
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message, Bot, MessageSegment
from nonebot.log import logger
from nonebot.params import CommandArg, ArgPlainText
from nonebot.typing import T_State

from .bupt_user import BUPTUser
from .config import Config

driver = get_driver()
plugin_config = Config.parse_obj(get_driver().config)
scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler

users = set()
checkin_times = set()
xisu_checkin_times = set()

add_new_user = on_command("add_new_user", aliases={"添加疫情打卡", "添加打卡"}, priority=5)
checkin = on_command("checkin", aliases={"打卡", "每日填报"}, priority=5)
checkin_pause = on_command("checkin_pause", aliases={"暂停打卡", "暂停每日填报", "恢复打卡", "恢复每日填报"}, priority=5)
xisu_checkin = on_command("xisu_checkin", aliases={"晨打卡", "晨午晚检"}, priority=5)
xisu_checkin_pause = on_command("xisu_checkin_pause", aliases={"暂停晨打卡", "暂停晨午晚检", "恢复晨打卡", "恢复晨午晚检"}, priority=5)
user_status = on_command("user_status", aliases={"用户情况", "用户状态"}, priority=5)
modify_checkin_time = on_command("modify_checkin_time", aliases={"修改打卡", "修改每日填报"}, priority=5)
modify_xisu_checkin_time = on_command("modify_xisu_checkin_time", aliases={"修改晨打卡", "修改晨午晚检"}, priority=5)

help = on_command("help_checkin", aliases={"疫情打卡帮助"}, priority=5)


@help.handle()
async def _():
    await help.finish("""
[BUPT ncov Bot] Help Menu
    "add_new_user", aliases={"添加疫情打卡", "添加打卡"}: Add a new user to sign in (In private chat)
    "checkin", aliases={"打卡", "每日填报"}: Checkin manually
    "checkin_pause", aliases={"暂停打卡", "暂停每日填报", "恢复打卡", "恢复每日填报"}: Switch on/off checkin function
    "xisu_checkin", aliases={"晨打卡", "晨午晚检"}: Xisu checkin manually
    "xisu_checkin_pause", aliases={"暂停晨打卡", "暂停晨午晚检", "恢复晨打卡", "恢复晨午晚检"}: Switch on/off xisu checkin function
    "user_status", aliases={"用户情况", "用户状态"}: Show status of checking bot
    "modify_checkin_time", aliases={"修改打卡", "修改每日填报"}: Change checkin time for yourself
    "modify_xisu_checkin_time", aliases={"修改晨打卡", "修改晨午晚检"}: Change xisu checkin time for yourself
    "help_checkin", aliases={"疫情打卡帮助"}: Show the help menu
    """)


@add_new_user.handle()
async def _(event: PrivateMessageEvent, state: T_State, command: Message = CommandArg()):
    if len(cmd := str(command).strip().split(" ")) == 2:
        state['username'] = Message(cmd[0])
        state['password'] = Message(cmd[1])


@add_new_user.got("username", prompt="What's your username?")
async def _():
    pass


@add_new_user.got("password", prompt="What's your password?")
async def _(event: PrivateMessageEvent, username: str = ArgPlainText("username"), password: str = ArgPlainText()):
    users.add(event.user_id)
    try:
        user = BUPTUser(event.user_id)
        user.get_or_create(username, password, force=True)

        msg = f"""Add Success!
        Username: {user.db.username}
        Checkin: 「{'Ⅹ' if user.db.is_stopped else '○'}」{user.db.checkin_time}
        Xisu_Checkin: 「{'Ⅹ' if user.db.is_xisu_stopped else '○'}」{user.db.xisu_checkin_time}
        """
        if user.db.checkin_time not in checkin_times:
            checkin_times.add(user.db.checkin_time)
        for each in user.db.xisu_checkin_time.split('|'):
            if each not in xisu_checkin_times:
                xisu_checkin_times.add(each)
        gen_new_scheduler()
        await add_new_user.finish(msg)
    except ConnectionError as e:
        await add_new_user.finish(f"[BUPT ncov Bot]{str(e)}")


@checkin.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        user = BUPTUser(event.user_id).get_or_create()
    except Exception as e:
        await bot.send(event, f"[BUPT ncov Bot]{str(e)}")
        return False
    await check(bot, user, 0)


@xisu_checkin.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        user = BUPTUser(event.user_id).get_or_create()
    except Exception as e:
        await bot.send(event, f"[BUPT ncov Bot]{str(e)}")
        return False
    await check(bot, user, 1)


@checkin_pause.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        user = BUPTUser(event.user_id).get_or_create()
    except Exception as e:
        await bot.send(event, f"[BUPT ncov Bot]{str(e)}")
        return False
    user.db.is_stopped = not user.db.is_stopped
    user.save()
    msg = f"""User Status
                    Username: {user.db.username}
                    Checkin: 「{'Ⅹ' if user.db.is_stopped else '○'}」{user.db.checkin_time}
                    Xisu_Checkin: 「{'Ⅹ' if user.db.is_xisu_stopped else '○'}」{user.db.xisu_checkin_time}
                    """
    await checkin_pause.finish(msg)


@xisu_checkin_pause.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        user = BUPTUser(event.user_id).get_or_create()
    except Exception as e:
        await bot.send(event, f"[BUPT ncov Bot]{str(e)}")
        return False
    user.db.is_xisu_stopped = not user.db.is_xisu_stopped
    user.save()
    msg = f"""User Status
                Username: {user.db.username}
                Checkin: 「{'Ⅹ' if user.db.is_stopped else '○'}」{user.db.checkin_time}
                Xisu_Checkin: 「{'Ⅹ' if user.db.is_xisu_stopped else '○'}」{user.db.xisu_checkin_time}
                """
    await xisu_checkin_pause.finish(msg)


@user_status.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        user = BUPTUser(event.user_id).get_or_create()
    except Exception as e:
        await bot.send(event, f"[BUPT ncov Bot]{str(e)}")
        return False
    msg = f"""User Status
            Username: {user.db.username}
            Checkin: 「{'Ⅹ' if user.db.is_stopped else '○'}」{user.db.checkin_time}
            Xisu_Checkin: 「{'Ⅹ' if user.db.is_xisu_stopped else '○'}」{user.db.xisu_checkin_time}
            """
    await user_status.finish(msg)


@modify_xisu_checkin_time.handle()
@modify_checkin_time.handle()
async def _(event: PrivateMessageEvent, state: T_State, command: Message = CommandArg()):
    if command:
        state['time'] = command


@modify_xisu_checkin_time.got('time',
                              prompt='When would you like to checkin? e.g `07:10|12:10|19:10` or `23:33|23:33|23:33`')
@modify_checkin_time.got('time', prompt='When would you like to checkin? e.g `07:10` or `23:33`')
async def _(bot: Bot, event: PrivateMessageEvent, time: str = ArgPlainText()):
    time = time.replace("：", ":")
    try:
        user = BUPTUser(event.user_id).get_or_create()
    except Exception as e:
        await bot.send(event, f"[BUPT ncov Bot]{str(e)}")
        return False
    if len(time.split("|")) == 3:
        old_times = xisu_checkin_times
        for each in time.split("|"):
            if not check_time_available(each):
                await bot.send(event,
                               "[BUPT ncov Bot]" + "Your Time Arg %s is not available!\ne.g `07:10` or `23:33`" % each)
                return False
            xisu_checkin_times.add(each)
        user.db.xisu_checkin_time = time
        user.save()
        if old_times is xisu_checkin_times:
            gen_new_scheduler()
    else:
        if not check_time_available(time.split("|")[0]):
            await bot.send(event,
                           "[BUPT ncov Bot]" + "Your Time Arg %s is not available!\ne.g `07:10` or `23:33`" %
                           time.split("|")[0])
            return False
        user.db.checkin_time = time.split("|")[0]
        user.save()
        if time.split("|")[0] not in checkin_times:
            checkin_times.add(time.split("|")[0])
            gen_new_scheduler()
    msg = f"""User Status
                Username: {user.db.username}
                Checkin: 「{'Ⅹ' if user.db.is_stopped else '○'}」{user.db.checkin_time}
                Xisu_Checkin: 「{'Ⅹ' if user.db.is_xisu_stopped else '○'}」{user.db.xisu_checkin_time}
                """

    await bot.send(event, msg)


def check_time_available(time_str: str) -> bool:
    if len(t := time_str.split(":")) == 2:
        if (
                t[0].isdigit()
                and (0 <= int(t[0]) < 24)
                and t[1].isdigit()
                and (0 <= int(t[1]) < 60)
        ):
            return True
    return False


async def check(bot: Bot, user: BUPTUser, type_: int = 0) -> bool:
    if not user.is_login:
        await bot.call_api("send_msg",
                           user_id=int(user.qq),
                           message=MessageSegment.text(
                               "[BUPT ncov Bot]Your bot is not login!\nplease reset the username and password"))
        return False
    try:
        msg = user.xisu_ncov_checkin() if type_ else user.ncov_checkin()
    except Exception as e:
        msg = str(e)
    await bot.call_api("send_msg",
                       user_id=int(user.qq),
                       message=MessageSegment.text(f"[BUPT ncov Bot]{msg}"))


async def scheduler_checkin(time: str, type_: int = 0):
    # Delete useless schedulers
    if type_:
        if time not in "|".join(BUPTUser(i).get_or_create().db.xisu_checkin_time for i in users):
            scheduler.remove_job(f"xisu_checkin{time}")
            xisu_checkin_times.remove(time)
            logger.info(scheduler.get_jobs())
            return

    elif time not in [BUPTUser(i).get_or_create().db.checkin_time for i in users]:
        scheduler.remove_job(f"checkin{time}")
        checkin_times.remove(time)
        logger.info(scheduler.get_jobs())
        return
    for i in users:
        user = BUPTUser(i).get_or_create()

        if type_:
            if not user.db.is_xisu_stopped and time in user.db.xisu_checkin_time:
                logger.info(f"Signing {i}")
                loop = get_running_loop()
                loop.call_later(randint(1, 100), check, get_bot(), user, type_)

        elif not user.db.is_stopped and time in user.db.checkin_time:
            logger.info(f"Signing {i}")
            loop = get_running_loop()
            loop.call_later(randint(1, 100), check, get_bot(), user, type_)


@driver.on_bot_connect
async def _():
    bot = get_bot()

    user = BUPTUser(0)

    for i in user.keys():
        users.add(i)
        new_user = BUPTUser(i)
        if (
                not new_user.get_or_create()
                and not new_user.db.is_stopped
                and not new_user.db.is_xisu_stopped
        ):
            await bot.call_api("send_msg",
                               user_id=int(i),
                               message=MessageSegment.text(
                                   "[BUPT ncov Bot]Your bot is not login!\nplease reset the username and password"))
        else:
            checkin_times.add(new_user.db.checkin_time)
            xisu_checkin_times.update(new_user.db.xisu_checkin_time.split('|'))
    gen_new_scheduler()


def gen_new_scheduler():
    for each in checkin_times:
        if f"checkin{each}" not in [i.id for i in scheduler.get_jobs()]:
            scheduler.add_job(
                scheduler_checkin,
                "cron",
                hour=each.split(':')[0],
                minute=each.split(':')[1],
                second=0,
                id=f"checkin{each}",
                args=[each, 0],
            )

    for each in xisu_checkin_times:
        if f"xisu_checkin{each}" not in [i.id for i in scheduler.get_jobs()]:
            scheduler.add_job(
                scheduler_checkin,
                "cron",
                hour=each.split(':')[0],
                minute=each.split(':')[1],
                second=1,
                id=f"xisu_checkin{each}",
                args=[each, 1],
            )

    logger.info(scheduler.get_jobs())
