from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Literal
from collections.abc import Callable, Awaitable

from nonebot_plugin_saa import Text, Image, MessageSegmentFactory

from nonebot_bison.theme import Theme
from nonebot_bison.utils import pic_merge, is_pics_mergable

if TYPE_CHECKING:
    from nonebot_bison.post import Post


class BasicTheme(Theme):
    """最基本的主题

    纯文本，应为每个Post必定支持的Theme
    """

    name: Literal["basic"] = "basic"

    async def render(
        self, post: "Post", content_handler: Callable[[str], Awaitable[str]] | None = None
    ) -> list[MessageSegmentFactory]:
        post_content = post.content
        if callable(content_handler):
            post_content = await content_handler(post_content)

        text = ""

        text += f"{post.title}\n\n" if post.title else ""

        text += post_content if len(post_content) < 500 else f"{post_content[:500]}..."

        if rp := post.repost:
            rp_content = rp.content
            if callable(content_handler):
                rp_content = await content_handler(rp_content)
            text += f"\n--------------\n转发自 {rp.nickname or ''}:\n"
            text += f"{rp.title}\n\n" if rp.title else ""
            text += rp_content if len(rp_content) < 500 else f"{rp_content[:500]}..."

        text += "\n--------------\n"

        text += f"来源: {post.platform.name} {post.nickname or ''}\n"

        urls: list[str] = []
        if rp and rp.url:
            urls.append(f"转发详情：{rp.url}")
        if post.url:
            urls.append(f"详情: {post.url}")

        if urls:
            text += "\n".join(urls)

        client = await post.platform.ctx.get_client_for_static()
        msgs: list[MessageSegmentFactory] = [Text(text)]

        pics_group: list[list[str | bytes | Path | BytesIO]] = []
        if post.images:
            pics_group.append(post.images)
        if rp and rp.images:
            pics_group.append(rp.images)

        for pics in pics_group:
            if is_pics_mergable(pics):
                pics = await pic_merge(list(pics), client)
            msgs.extend(map(Image, pics))

        return msgs
