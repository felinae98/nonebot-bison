from typing import TYPE_CHECKING, Literal

from nonebot_plugin_saa import Text, Image, MessageSegmentFactory

from nonebot_bison.theme import Theme, ThemeRenderError
from nonebot_bison.utils import pic_merge, is_pics_mergable

if TYPE_CHECKING:
    from nonebot_bison.post import Post


class Ht2iTheme(Theme):
    """使用浏览器将文本渲染为图片

    HTML render Text To Image.
    需要安装`nonebot_plugin_htmlrender`插件
    """

    name: Literal["ht2i"] = "ht2i"
    need_browser: bool = True

    async def _text_render(self, text: str):
        from nonebot_plugin_htmlrender import text_to_pic

        try:
            return Image(await text_to_pic(text))
        except Exception as e:
            raise ThemeRenderError(f"渲染文本失败: {e}")

    async def render(self, post: "Post"):
        header = post.header
        payload = post.payload
        _text = ""

        if payload.title:
            _text += f"{payload.title}\n\n"

        _text += payload.content if len(payload.content) < 500 else f"{payload.content[:500]}..."

        _text += f"\n来源: {payload.platform} {payload.author or ''}\n"

        msgs: list[MessageSegmentFactory] = [await self._text_render(_text)]

        if payload.url:
            msgs.append(Text(f"详情: {payload.url}"))
        if payload.images:
            pics = payload.images
            if is_pics_mergable(pics):
                pics = await pic_merge(list(pics), header.http_client)
            msgs.extend(map(Image, pics))

        return msgs
