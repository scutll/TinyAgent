# image_filter.py

from PIL import Image

def is_useful_image(
    image: Image.Image,
    image_bytes: bytes,
    *,
    min_width: int = 100,
    min_height: int = 100,
    min_size_bytes: int = 5 * 1024,
    max_aspect_ratio: float = 8.0,
    is_background: bool = False
) -> bool:
    """
    判断一张 PPT 图片是否值得保留（非装饰性）

    Parameters:
        image: PIL Image 对象
        image_bytes: 原始图片字节
        min_width: 最小宽度
        min_height: 最小高度
        min_size_bytes: 最小文件体积
        max_aspect_ratio: 最大宽高比
        is_background: 是否来自母版/背景

    Returns:
        bool: True 表示保留，False 表示过滤
    """

    # 1️⃣ 背景图直接过滤
    if is_background:
        return False

    width, height = image.size

    # 2️⃣ 尺寸过滤
    if width < min_width or height < min_height:
        return False

    # 3️⃣ 文件大小过滤
    if len(image_bytes) < min_size_bytes:
        return False

    # 4️⃣ 长宽比过滤（过滤横线/竖线）
    ratio = max(width / height, height / width)
    if ratio > max_aspect_ratio:
        return False

    return True
