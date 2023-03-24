import asyncio
import typing

import pytest
from flaky import flaky
from nonebot_plugin_saa.nonebug import should_send_saa
from nonebug import App
from pytest_mock.plugin import MockerFixture


@pytest.mark.asyncio
async def test_send_no_queue(app: App, mocker: MockerFixture):
    from nonebot.adapters.onebot.v11.bot import Bot
    from nonebot_plugin_saa import MessageFactory, TargetQQGroup, TargetQQPrivate

    from nonebot_bison.plugin_config import plugin_config
    from nonebot_bison.send import send_msgs

    mocker.patch.object(plugin_config, "bison_use_queue", False)

    group_target = TargetQQGroup(group_id=1233)
    private_target = TargetQQPrivate(user_id=666)

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot)
        assert isinstance(bot, Bot)
        should_send_saa(ctx, MessageFactory("msg1"), bot, target=group_target)
        should_send_saa(ctx, MessageFactory("msg2"), bot, target=group_target)
        should_send_saa(ctx, MessageFactory("priv"), bot, target=private_target)
        await send_msgs(
            bot, group_target, [MessageFactory("msg1"), MessageFactory("msg2")]
        )
        await send_msgs(bot, private_target, [MessageFactory("priv")])
        assert ctx.wait_list.empty()


@pytest.mark.asyncio
async def test_send_queue(app: App, mocker: MockerFixture):
    import nonebot
    from nonebot.adapters.onebot.v11.bot import Bot
    from nonebot_plugin_saa import MessageFactory, TargetQQGroup

    from nonebot_bison.plugin_config import plugin_config
    from nonebot_bison.send import MESSGE_SEND_INTERVAL, send_msgs

    mocker.patch.object(plugin_config, "bison_use_queue", True)
    async with app.test_api() as ctx:
        new_bot = ctx.create_bot(base=Bot)
        mocker.patch.object(nonebot, "get_bot", lambda: new_bot)
        bot = nonebot.get_bot()
        assert isinstance(bot, Bot)
        assert bot == new_bot

        target = TargetQQGroup(group_id=1233)
        should_send_saa(ctx, MessageFactory("msg"), bot, target=target)
        should_send_saa(ctx, MessageFactory("msg2"), bot, target=target)

        await send_msgs(bot, target, [MessageFactory("msg")])
        await send_msgs(bot, target, [MessageFactory("msg2")])
        assert not ctx.wait_list.empty()
        await asyncio.sleep(2 * MESSGE_SEND_INTERVAL)
        assert ctx.wait_list.empty()


@pytest.mark.asyncio
async def test_send_merge_no_queue(app: App):
    from nonebot.adapters.onebot.v11.bot import Bot
    from nonebot_plugin_saa import (
        AggregatedMessageFactory,
        Image,
        MessageFactory,
        TargetQQGroup,
        Text,
    )

    from nonebot_bison.plugin_config import plugin_config
    from nonebot_bison.send import send_msgs

    plugin_config.bison_use_pic_merge = 1
    plugin_config.bison_use_queue = False

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, self_id="8888")
        assert isinstance(bot, Bot)
        target = TargetQQGroup(group_id=633)

        message = [
            MessageFactory(Text("test msg")),
            MessageFactory(Image("https://picsum.photos/200/300")),
        ]
        should_send_saa(ctx, message[0], bot, target=target)
        should_send_saa(ctx, message[1], bot, target=target)
        await send_msgs(bot, target, message)

        message = [
            MessageFactory(Text("test msg")),
            MessageFactory(Image("https://picsum.photos/200/300")),
            MessageFactory(Image("https://picsum.photos/200/300")),
        ]
        should_send_saa(ctx, message[0], bot, target=target)
        should_send_saa(ctx, AggregatedMessageFactory(message[1:]), bot, target=target)
        # import ipdb; ipdb.set_trace()
        await send_msgs(bot, target, message)

        message = [
            MessageFactory(Text("test msg")),
            MessageFactory(Image("https://picsum.photos/200/300")),
            MessageFactory(Image("https://picsum.photos/200/300")),
            MessageFactory(Image("https://picsum.photos/200/300")),
        ]
        should_send_saa(ctx, message[0], bot, target=target)
        should_send_saa(ctx, AggregatedMessageFactory(message[1:]), bot, target=target)
        await send_msgs(bot, target, message)


async def test_send_merge2_no_queue(app: App):
    from nonebot.adapters.onebot.v11.bot import Bot
    from nonebot_plugin_saa import (
        AggregatedMessageFactory,
        Image,
        MessageFactory,
        TargetQQGroup,
        Text,
    )

    from nonebot_bison.plugin_config import plugin_config
    from nonebot_bison.send import send_msgs

    plugin_config.bison_use_pic_merge = 2
    plugin_config.bison_use_queue = False

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, self_id="8888")
        assert isinstance(bot, Bot)
        target = TargetQQGroup(group_id=633)

        message = [
            MessageFactory(Text("test msg")),
            MessageFactory(Image("https://picsum.photos/200/300")),
            MessageFactory(Image("https://picsum.photos/200/300")),
        ]
        should_send_saa(ctx, AggregatedMessageFactory(message), bot, target=target)
        await send_msgs(bot, target, message)
