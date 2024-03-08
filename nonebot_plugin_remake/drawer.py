from io import BytesIO
from pathlib import Path
from typing import List, NamedTuple, Optional

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as IMG
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from .life import PerAgeProperty, PerAgeResult
from .property import PropSummary, Summary
from .talent import Talent

resource_dir = Path(__file__).parent / "resources"
image_dir = resource_dir / "images"
font_dir = resource_dir / "fonts"
font_path = str(font_dir / "方正像素12.ttf")


def get_font(fontsize: int) -> FreeTypeFont:
    return ImageFont.truetype(str(font_dir / "方正像素12.ttf"), fontsize)


def get_icon(item: str) -> IMG:
    return Image.open(image_dir / f"icon_{item}.png")


def break_text(text: str, font: FreeTypeFont, length: int) -> List[str]:
    lines = []
    line = ""
    for word in text:
        if font.getlength(line + word) > length:
            lines.append(line)
            line = ""
        line += word
    if line:
        lines.append(line)
    return lines


def text_to_image(
    texts: List[str],
    fontsize: int = 10,
    fill: str = "black",
    spacing: int = 4,
    max_width: Optional[int] = None,
) -> IMG:
    font = get_font(fontsize)
    texts = sum([text.splitlines() for text in texts], [])
    if max_width:
        texts = sum([break_text(text, font, max_width) for text in texts], [])
    max_length = int(max([font.getlength(text) for text in texts]))
    ascent, descent = font.getmetrics()
    h = ascent * len(texts) + spacing * (len(texts) - 1) + descent
    image = Image.new("RGBA", (max_length, h))
    draw = ImageDraw.Draw(image)
    text = "\n".join(texts)
    draw.multiline_text((0, 0), text, font=font, fill=fill, spacing=spacing)
    return image


def draw_init_properties(prop: PerAgeProperty) -> IMG:
    image = Image.new("RGBA", (1250, 84))
    font = get_font(45)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width, image.height), 20, "#0A2530")
    x = 0

    def draw_property(item: str, name: str, value: int):
        nonlocal x
        icon = get_icon(item)
        image.paste(
            icon, (x + (84 - icon.width) // 2, (84 - icon.height) // 2), mask=icon
        )
        draw.text((x + 84, 18), name, font=font, fill="white")
        length = font.getlength(str(value))
        draw.text(
            (x + 170 + (80 - length) // 2, 18), str(value), font=font, fill="#53F8F8"
        )
        x += 250

    draw_property("chr", "颜值", prop.CHR)
    draw_property("int", "智力", prop.INT)
    draw_property("str", "体质", prop.STR)
    draw_property("mny", "家境", prop.MNY)
    draw_property("spr", "快乐", prop.SPR)
    return image


def draw_properties(prop: PerAgeProperty) -> IMG:
    image = Image.new("RGBA", (670, 84))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width, image.height), 20, "#153D4F")
    font = get_font(45)
    x = 0

    def draw_property(item: str, value: int):
        nonlocal x
        icon = get_icon(item)
        image.paste(
            icon, (x + (84 - icon.width) // 2, (84 - icon.height) // 2), mask=icon
        )
        x += 84
        w = font.getlength(str(value))
        draw.text((x + (46 - w) // 2, 18), str(value), font=font, fill="#53F8F8")
        x += 46

    draw_property("chr", prop.CHR)
    draw_property("int", prop.INT)
    draw_property("str", prop.STR)
    draw_property("mny", prop.MNY)
    draw_property("spr", prop.SPR)
    return image


def draw_age(age: int) -> IMG:
    return text_to_image([f"{age}岁："], fontsize=45, fill="#C3DE5A")


def draw_logs(logs: List[str]) -> IMG:
    return text_to_image(logs, fontsize=45, fill="#F0F2F3", spacing=30, max_width=1200)


def draw_results(results: List[PerAgeResult]) -> IMG:
    margin_prop = 20
    margin_logs = 50

    class ImageResult(NamedTuple):
        prop: IMG
        age: IMG
        logs: IMG

        @property
        def width(self) -> int:
            return max(self.prop.width, self.age.width + self.logs.width)

        @property
        def height(self) -> int:
            return (
                self.prop.height + margin_prop + max(self.age.height, self.logs.height)
            )

    images: List[ImageResult] = []
    for result in results:
        image_prop = draw_properties(result.property)
        image_prop = image_prop.resize(
            (image_prop.width * 2 // 3, image_prop.height * 2 // 3), Resampling.LANCZOS
        )
        image_age = draw_age(result.property.AGE)
        image_logs = draw_logs(result.event_log + result.talent_log)
        images.append(ImageResult(image_prop, image_age, image_logs))

    image_groups: List[List[ImageResult]] = []
    max_height = 10000
    sum_height = sum(image.height for image in images) + margin_logs * (len(images) - 1)
    num_groups = (sum_height - 1) // max_height + 1
    results_height = sum_height // num_groups
    if num_groups > 1:
        results_height += max(image.height for image in images)

    img_h = 0
    temp_images: List[ImageResult] = []
    for image in images:
        if img_h + image.height > results_height:
            image_groups.append(temp_images)
            temp_images = []
            max_height = max(max_height, img_h - margin_logs)
            img_h = 0
        img_h += image.height + margin_logs
        temp_images.append(image)
    if temp_images:
        image_groups.append(temp_images)
        max_height = max(max_height, img_h - margin_logs)

    margin_group = 100
    img_w = sum(
        max(image.width for image in image_group) for image_group in image_groups
    ) + margin_group * (len(image_groups) - 1)
    img_h = max(
        sum(image.height for image in image_group)
        + margin_logs * (len(image_group) - 1)
        for image_group in image_groups
    )
    img = Image.new("RGBA", (img_w, img_h))
    x = 0
    y = 0
    for image_group in image_groups:
        img_w = max(image.width for image in image_group)
        age_w = max([image.age.width for image in image_group])
        for image in image_group:
            img.paste(image.prop, (x, y), mask=image.prop)
            y += image.prop.height + margin_prop
            img.paste(image.age, (x + age_w - image.age.width, y), mask=image.age)
            img.paste(image.logs, (x + age_w, y), mask=image.logs)
            y += max(image.logs.height, image.age.height) + margin_logs
        x += img_w + margin_group
        y = 0

    padding = 50
    inner_w = img.width + padding * 2
    inner_h = img.height + padding * 2
    inner_w = max(inner_w, 1250)
    inner = Image.new("RGBA", (inner_w, inner_h), "#0A2530")
    inner.paste(img, (padding, padding), mask=img)

    margin = 6
    border = Image.new("RGBA", (inner.width + margin * 2, inner.height + margin * 2))
    draw = ImageDraw.Draw(border)
    draw.rectangle(
        (margin, margin, border.width - margin, border.height - margin),
        outline="#267674",
        width=2,
    )

    length = 100
    rect = Image.new("RGBA", (length * 2, length * 2))
    draw = ImageDraw.Draw(rect)
    draw.rectangle((0, 0, rect.width, rect.height), outline="#267674", width=margin)
    for crop_box, pos in (
        ((0, 0, length, length), (0, 0)),
        ((length, 0, length * 2, length), (border.width - length, 0)),
        ((0, length, length, length * 2), (0, border.height - length)),
        (
            (length, length, length * 2, length * 2),
            (border.width - length, border.height - length),
        ),
    ):
        corner = rect.crop(crop_box)
        border.paste(corner, pos, mask=corner)

    frame = Image.new("RGBA", (border.width, border.height))
    frame.paste(inner, (margin, margin), mask=inner)
    frame.paste(border, (0, 0), mask=border)
    return frame


def grade_color(grade: int) -> str:
    if grade == 3:
        return "#FDCD44"
    elif grade == 2:
        return "#AC7AF9"
    elif grade == 1:
        return "#54FDFC"
    else:
        return "#CACBCB"


def draw_progress_bar(item: str, summary: PropSummary) -> IMG:
    def draw_progress(value: int, color: str) -> IMG:
        image = Image.new("RGBA", (770, 40))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, image.width, image.height), fill="#273D47")
        count = min(max(value, 0), 10)
        draw.rectangle((0, 0, image.width * count // 10, image.height), fill=color)
        font = get_font(40)
        length = font.getlength(str(value))
        draw.text(
            ((image.width - length) // 2, 0),
            str(value),
            font=font,
            fill=color,
            stroke_width=2,
            stroke_fill="black",
        )
        return image

    image = Image.new("RGBA", (1200, 84))
    icon = get_icon(item)
    image.paste(icon, ((84 - icon.width) // 2, (84 - icon.height) // 2), mask=icon)
    draw = ImageDraw.Draw(image)
    font = get_font(45)
    draw.text((84, 18), summary.name, font=font, fill="white")
    color = grade_color(summary.grade)
    progress = draw_progress(summary.value, color)
    image.paste(progress, (200, (image.height - progress.height) // 2), mask=progress)
    judge = summary.judge
    length = font.getlength(judge)
    draw.text(
        (200 + progress.width + (230 - length) // 2, 18), judge, font=font, fill=color
    )
    return image


def draw_summary(summary: Summary) -> IMG:
    def draw_sum(prop_sum: PropSummary) -> IMG:
        image = Image.new("RGBA", (1000, 84))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, 300, image.height), 20, "#153D4F")
        font = get_font(45)
        draw.text((20, 18), f"{prop_sum.name}：", font=font, fill="white")
        length = font.getlength(str(prop_sum.value))
        draw.text(
            (140 + (160 - length) // 2, 18),
            str(prop_sum.value),
            font=font,
            fill="#53F8F8",
        )
        color = grade_color(prop_sum.grade)
        length = font.getlength(prop_sum.judge)
        draw.text(
            (770 + (230 - length) // 2, 18), prop_sum.judge, font=font, fill=color
        )
        return image

    inner = Image.new("RGBA", (1200, 650))
    image_age = draw_sum(summary.AGE)
    image_sum = draw_sum(summary.SUM)
    inner.paste(image_age, (200, 0), mask=image_age)
    inner.paste(image_sum, (200, 110), mask=image_sum)
    progress_bars = [
        draw_progress_bar("chr", summary.CHR),
        draw_progress_bar("int", summary.INT),
        draw_progress_bar("str", summary.STR),
        draw_progress_bar("mny", summary.MNY),
        draw_progress_bar("spr", summary.SPR),
    ]
    y = 230
    for progress_bar in progress_bars:
        inner.paste(progress_bar, (0, y), mask=progress_bar)
        y += progress_bar.height

    bg = Image.open(image_dir / "bg_summary.png")
    bg.paste(
        inner,
        ((bg.width - inner.width) // 2, (bg.height - inner.height) // 2),
        mask=inner,
    )
    return bg


def draw_title(text: str) -> IMG:
    titlebar = Image.open(image_dir / "titlebar.png")
    font = get_font(50)
    length = font.getlength(text)
    draw = ImageDraw.Draw(titlebar)
    draw.text(
        ((titlebar.width - length) // 2, 130),
        text,
        font=font,
        fill="white",
    )
    left = Image.open(image_dir / "title_left.png")
    right = Image.open(image_dir / "title_right.png")
    titlebar.paste(
        left, (int((titlebar.width - length) / 2 - left.width - 10), 140), mask=left
    )
    titlebar.paste(right, (int((titlebar.width + length) / 2 + 10), 140), mask=right)
    return titlebar


def draw_talent(talent: Talent) -> IMG:
    bg = Image.open(image_dir / "bg_talent.png")
    font = get_font(45)
    draw = ImageDraw.Draw(bg)
    draw.text((40, 50), talent.name, font=font, fill="white")
    font = get_font(35)
    text = "\n".join(break_text(talent.description, font, 300))
    draw.multiline_text((40, 130), text, font=font, fill="#879A9E", spacing=10)
    return bg


def draw_talents(talents: List[Talent]) -> IMG:
    talent_images = [draw_talent(t) for t in talents]
    talent_w = talent_images[0].width
    talent_h = talent_images[0].height
    margin = 30
    image = Image.new("RGBA", (talent_w * 3 + margin * 2, talent_h))
    x = 0
    for talent_image in talent_images:
        image.paste(talent_image, (x, 0), mask=talent_image)
        x += talent_w + margin
    return image


def draw_life(
    talents: List[Talent],
    init_prop: PerAgeProperty,
    results: List[PerAgeResult],
    summary: Summary,
) -> IMG:
    images: List[IMG] = []
    images.append(draw_title("已选天赋"))
    images.append(draw_talents(talents))
    images.append(draw_title("初始属性"))
    images.append(draw_init_properties(init_prop))
    images.append(draw_title("人生经历"))
    images.append(draw_results(results))
    images.append(draw_title("人生总结"))
    images.append(draw_summary(summary))

    img_w = max([image.width for image in images])
    img_h = sum([image.height for image in images]) + 100
    margin = 50
    frame = Image.new("RGBA", (img_w + margin * 2, img_h + margin * 2), "#04131F")
    y = margin
    for image in images:
        frame.paste(image, (margin + (img_w - image.width) // 2, y), mask=image)
        y += image.height
    return frame


def save_jpg(img: IMG) -> BytesIO:
    output = BytesIO()
    img.convert("RGB").save(output, format="JPEG")
    return output
