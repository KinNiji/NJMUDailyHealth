import os
import traceback

import nonebot
from loguru import logger

from .net import DailyHealth


async def one_config(config_path):
    bot = nonebot.get_bot()
    daily_health = DailyHealth(config_path)
    await bot.send_private_msg(
        user_id=daily_health.qq_id,
        message='操作执行中...')
    try:
        return_message = await daily_health.core.web_actions()
        await bot.send_private_msg(
            user_id=daily_health.qq_id,
            message=f'学号{daily_health.user_id}操作完成\n'
                    f'返回信息：{return_message}')
    except Exception as e:
        logger.warning(f'str(e): {str(e)}\n\n'
                       f'repr(e): {repr(e)}\n\n'
                       f'e.args: {e.args}\n\n'
                       f'traceback.print_exc(): {traceback.print_exc()}\n\n'
                       f'traceback.format_exc(): {traceback.format_exc()}')
        await bot.send_private_msg(
            user_id=daily_health.qq_id,
            message=f'学号{daily_health.user_id}填报失败！\n'
                    f'异常信息：\n'
                    f'str(e): {str(e)}\n'
                    f'repr(e): {repr(e)}\n'
                    f'e.args: {e.args}\n'
                    f'更多异常信息请查看控制台。')
    finally:
        await daily_health.core.quit()


@nonebot.scheduler.scheduled_job('cron', hour=7)
async def _():
    await one_config(os.getcwd() + '/plugins/daily_health/config/config.json')


@nonebot.on_command('daily_health_on_command', aliases=('健康打卡', '健康日报打卡', '健康信息每日打卡'))
async def _(session: nonebot.CommandSession):
    await one_config(os.getcwd() + '/plugins/daily_health/config/config.json')
