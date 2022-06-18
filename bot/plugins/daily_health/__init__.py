import os
import time
import traceback

import nonebot
from loguru import logger
from nonebot import SenderRoles

from .net import DailyHealth

bot = nonebot.get_bot()


def get_file_list():
    config_dir = os.getcwd() + '/bot/plugins/daily_health/config/'
    file_list = []
    file_name_list = []
    for file_name in os.listdir(config_dir):
        file_list.append(config_dir + file_name)
        file_name_list.append(file_name.split('.')[0])
    return file_list, file_name_list


def permission_check(sender: SenderRoles):
    return sender.is_groupchat  # and (sender.is_admin or sender.is_owner)


async def one_config(config_path):
    daily_health = DailyHealth(config_path)
    await bot.send_group_msg(
        group_id=661553440,
        message=f'[CQ:at,qq={daily_health.qq_id}]学号{daily_health.user_id}操作执行中...')
    try:
        return_message = await daily_health.core.web_actions()
        await bot.send_group_msg(
            group_id=661553440,
            message=f'[CQ:at,qq={daily_health.qq_id}]学号{daily_health.user_id}操作执行成功！\n'
                    f'返回信息：{return_message}')
    except Exception as e:
        logger.warning(f'str(e): {str(e)}\n\n'
                       f'repr(e): {repr(e)}\n\n'
                       f'e.args: {e.args}\n\n'
                       f'traceback.print_exc(): {traceback.print_exc()}\n\n'
                       f'traceback.format_exc(): {traceback.format_exc()}')
        await bot.send_group_msg(
            group_id=661553440,
            message=f'[CQ:at,qq={daily_health.qq_id}]学号{daily_health.user_id}操作执行失败！\n'
                    f'异常信息：{type(e)}\n'
                    f'更多异常信息请查看控制台。')
    finally:
        await daily_health.core.quit()


@nonebot.scheduler.scheduled_job('cron', hour=7)
async def _():
    file_list, file_name_list = get_file_list()
    file_name_list_str = '\n'.join(file_name_list)
    await bot.send_group_msg(
        group_id=661553440,
        message=f'定时操作开始执行\n'
                f'当前时间：{time.asctime(time.localtime(time.time()))}\n'
                f'本次配置文件包括：\n'
                f'{file_name_list_str}')
    for file_path in file_list:
        await one_config(file_path)


@nonebot.on_command('daily_health', aliases='健康打卡', only_to_me=False)
async def _(session: nonebot.CommandSession):
    stu_id = session.current_arg_text.strip()
    if not stu_id:
        stu_id = (await session.send('请输入要打卡的学号')).strip()
        while not stu_id:
            stu_id = (await session.aget(prompt='文本不能为空，请重新输入')).strip()

    file_list, file_name_list = get_file_list()
    if stu_id not in file_name_list:
        await bot.send_group_msg(
            group_id=661553440,
            message=f'未找到您的配置文件。\n'
                    f'请在http://124.222.18.67/上传配置文件。')
    else:
        await bot.send_group_msg(
            group_id=661553440,
            message=f'命令操作开始执行\n'
                    f'当前时间：{time.asctime(time.localtime(time.time()))}')
        await one_config(file_list[file_name_list.index(stu_id)])


@nonebot.on_command('check_config', only_to_me=False)
async def _(session: nonebot.CommandSession):
    file_list, file_name_list = get_file_list()
    file_name_list_str = '\n'.join(file_name_list)
    await bot.send_group_msg(
        group_id=661553440,
        message=f'all configs：\n'
                f'{file_name_list_str}')


@nonebot.on_command('delete_config', only_to_me=False, permission=permission_check)
async def _(session: nonebot.CommandSession):
    stu_id = session.current_arg_text.strip()
    if not stu_id:
        stu_id = (await session.send('please enter stu_id.')).strip()
        while not stu_id:
            stu_id = (await session.aget(prompt="stu_id can't be blank, try again.")).strip()

    file_list, file_name_list = get_file_list()
    if stu_id not in file_name_list:
        await bot.send_group_msg(
            group_id=661553440,
            message=f'config not exist: {stu_id}')
    else:
        os.remove(file_list[file_name_list.index(stu_id)])
        await bot.send_group_msg(
            group_id=661553440,
            message=f'config delete successfully: {stu_id}')
