from typing import cast

from nonebot.log import logger
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER

from ..utils import Site
from ..config import config
from .scheduler import Scheduler
from .statistic import runtime_statistic
from ..config.db_model import Target
from ..types import Target as T_Target
from ..platform import platform_manager
from ..plugin_config import plugin_config
from ..utils.site import CookieClientManager, is_cookie_client_manager

inspect_scheduler = on_command("inspect-bison", priority=5, rule=to_me(), permission=SUPERUSER)
scheduler_dict: dict[type[Site], Scheduler] = {}


async def init_scheduler():
    _schedule_class_dict: dict[type[Site], list[Target]] = {}
    _schedule_class_platform_dict: dict[type[Site], list[str]] = {}
    for platform in platform_manager.values():
        site = platform.site
        if not hasattr(site, "name") or not site.name:
            site.name = f"AnonymousScheduleConfig[{platform.platform_name}]"

        platform_name = platform.platform_name
        targets = await config.get_platform_target(platform_name)
        if site not in _schedule_class_dict:
            _schedule_class_dict[site] = list(targets)
        else:
            _schedule_class_dict[site].extend(targets)
        if site not in _schedule_class_platform_dict:
            _schedule_class_platform_dict[site] = [platform_name]
        else:
            _schedule_class_platform_dict[site].append(platform_name)
    for site, target_list in _schedule_class_dict.items():
        if not plugin_config.bison_use_browser and site.require_browser:
            logger.warning(f"{site.name} requires browser, it will not schedule.")
            continue

        schedulable_args = []
        for target in target_list:
            schedulable_args.append(
                (target.platform_name, T_Target(target.target), platform_manager[target.platform_name].use_batch)
            )
        platform_name_list = _schedule_class_platform_dict[site]
        scheduler_dict[site] = Scheduler(site, schedulable_args, platform_name_list)
        if is_cookie_client_manager(site.client_mgr):
            client_mgr = cast(CookieClientManager, scheduler_dict[site].client_mgr)
            await client_mgr.refresh_client()
    config.register_add_target_hook(handle_insert_new_target)
    config.register_delete_target_hook(handle_delete_target)


async def handle_insert_new_target(platform_name: str, target: T_Target):
    platform = platform_manager[platform_name]
    scheduler_obj = scheduler_dict[platform.site]
    scheduler_obj.insert_new_schedulable(platform_name, target)


async def handle_delete_target(platform_name: str, target: T_Target):
    if platform_name not in platform_manager:
        return
    platform = platform_manager[platform_name]
    scheduler_obj = scheduler_dict[platform.site]
    scheduler_obj.delete_schedulable(platform_name, target)

@inspect_scheduler.handle()
async def inspect_scheduler_handle():
    report = runtime_statistic.generate_report(scheduler_dict)
    await inspect_scheduler.send("统计数据仅为本次启动后的数据，不包含历史数据")
    await inspect_scheduler.finish(report)
