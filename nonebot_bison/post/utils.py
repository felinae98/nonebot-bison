from io import BytesIO

from PIL import Image
from nonebot.log import logger

from ..utils import http_client


async def _pic_url_to_image(data: str | bytes) -> Image.Image:
    pic_buffer = BytesIO()
    if isinstance(data, str):
        async with http_client() as client:
            res = await client.get(data)
        pic_buffer.write(res.content)
    else:
        pic_buffer.write(data)
    return Image.open(pic_buffer)


def _check_image_square(size: tuple[int, int]) -> bool:
    return abs(size[0] - size[1]) / size[0] < 0.05


async def pic_merge(pics: list[str | bytes]) -> list[str | bytes]:
    if len(pics) < 3:
        return pics
    first_image = await _pic_url_to_image(pics[0])
    if not _check_image_square(first_image.size):
        return pics
    images: list[Image.Image] = [first_image]
    # first row
    for i in range(1, 3):
        cur_img = await _pic_url_to_image(pics[i])
        if not _check_image_square(cur_img.size):
            return pics
        if cur_img.size[1] != images[0].size[1]:  # height not equal
            return pics
        images.append(cur_img)
    _tmp = 0
    x_coord = [0]
    for i in range(3):
        _tmp += images[i].size[0]
        x_coord.append(_tmp)
    y_coord = [0, first_image.size[1]]

    async def process_row(row: int) -> bool:
        if len(pics) < (row + 1) * 3:
            return False
        row_first_img = await _pic_url_to_image(pics[row * 3])
        if not _check_image_square(row_first_img.size):
            return False
        if row_first_img.size[0] != images[0].size[0]:
            return False
        image_row: list[Image.Image] = [row_first_img]
        for i in range(row * 3 + 1, row * 3 + 3):
            cur_img = await _pic_url_to_image(pics[i])
            if not _check_image_square(cur_img.size):
                return False
            if cur_img.size[1] != row_first_img.size[1]:
                return False
            if cur_img.size[0] != images[i % 3].size[0]:
                return False
            image_row.append(cur_img)
        images.extend(image_row)
        y_coord.append(y_coord[-1] + row_first_img.size[1])
        return True

    if await process_row(1):
        matrix = (3, 2)
    else:
        matrix = (3, 1)
    if await process_row(2):
        matrix = (3, 3)
    logger.info("trigger merge image")
    target = Image.new("RGB", (x_coord[-1], y_coord[-1]))
    for y in range(matrix[1]):
        for x in range(matrix[0]):
            target.paste(
                images[y * matrix[0] + x],
                (x_coord[x], y_coord[y], x_coord[x + 1], y_coord[y + 1]),
            )
    target_io = BytesIO()
    target.save(target_io, "JPEG")
    pics = pics[matrix[0] * matrix[1] :]
    pics.insert(0, target_io.getvalue())
    return pics