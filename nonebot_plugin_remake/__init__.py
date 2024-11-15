import itertools
import random
import re
import traceback
from io import BytesIO
from typing import Optional

from nonebot import require
from nonebot.adapters import Event
from nonebot.exception import AdapterException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.rule import to_me
from nonebot.utils import run_sync

require("nonebot_plugin_alconna")
require("nonebot_plugin_waiter")

from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Option,
    Query,
    UniMessage,
    on_alconna,
    store_true,
)
from nonebot_plugin_waiter import waiter

from .drawer import draw_life, save_jpg
from .life import Life, PerAgeProperty, PerAgeResult
from .property import Summary
from .talent import Talent

__plugin_meta__ = PluginMetadata(
    name="人生重开",
    description="人生重开模拟器",
    usage="@我 remake/liferestart/人生重开",
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-remake",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)


matcher_remake = on_alconna(
    Alconna(
        "remake",
        Option(
            "--random|随机",
            default=False,
            action=store_true,
            help_text="随机选择天赋和属性",
        ),
    ),
    aliases={"liferestart", "人生重开", "人生重来"},
    block=True,
    rule=to_me(),
    use_cmd_start=True,
    priority=12,
)
matcher_remake.shortcut("随机人生", arguments=["--random"], prefix=True)


@matcher_remake.handle()
async def _(
    matcher: Matcher,
    random_life: Query[bool] = AlconnaQuery("random.value", False),
):
    life = Life()
    life.load()
    talents = life.rand_talents(10)

    @waiter(waits=["message"], keep_session=True)
    async def get_response(event: Event):
        logger.debug(event.get_message())
        return event.get_plaintext()

    def conflict_talents(talents: list[Talent]) -> Optional[tuple[Talent, Talent]]:
        for t1, t2 in itertools.combinations(talents, 2):
            if t1.exclusive_with(t2):
                return t1, t2
        return None

    def random_talents():
        while True:
            nums = random.sample(range(10), 3)
            nums.sort()
            talents_selected = [talents[n] for n in nums]
            if not conflict_talents(talents_selected):
                break
        return talents_selected

    async def select_talents():
        for _ in range(3):
            resp = await get_response.wait(timeout=30)
            if resp is None:
                await matcher.finish("人生重开已取消")

            elif matched := re.fullmatch(r"\s*(\d)\s*(\d)\s*(\d)\s*", resp):
                nums = list(matched.groups())
                nums = [int(n) for n in nums]
                nums.sort()
                if nums[-1] >= 10:
                    await matcher.send("请发送正确的编号")
                talents_selected = [talents[n] for n in nums]
                if conflict := conflict_talents(talents_selected):
                    await matcher.send(
                        f"你选择的天赋“{conflict[0].name}”和“{conflict[1].name}”不能同时拥有，请重新选择"
                    )
                return talents_selected

            elif re.fullmatch(r"[\d\s]+", resp):
                await matcher.send("请发送正确的编号，如“0 1 2”")
                continue

            elif resp == "随机":
                return random_talents()

            else:
                await matcher.finish("人生重开已取消")

    if random_life.result:
        talents_selected = random_talents()
    else:
        msg = "请发送编号选择3个天赋，如“0 1 2”，或发送“随机”随机选择"
        des = "\n".join([f"{i}.{t}" for i, t in enumerate(talents)])
        await matcher.send(f"{msg}\n\n{des}")
        talents_selected = await select_talents()

        if talents_selected is None:
            await matcher.finish("人生重开已取消")

    life.set_talents(talents_selected)
    total_prop = life.total_property()

    def random_nums():
        half_prop1 = int(total_prop / 2)
        half_prop2 = total_prop - half_prop1
        num1 = random.randint(0, half_prop1)
        num2 = random.randint(0, half_prop2)
        nums = [num1, num2, half_prop1 - num1, half_prop2 - num2]
        random.shuffle(nums)
        return nums

    async def select_nums():
        for _ in range(3):
            resp = await get_response.wait(timeout=30)
            if resp is None:
                await matcher.finish()

            elif matched := re.fullmatch(
                r"\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*", resp
            ):
                nums = list(matched.groups())
                nums = [int(n) for n in nums]
                if sum(nums) != total_prop:
                    await matcher.send(f"属性之和需为{total_prop}，请重新发送")
                    continue
                elif max(nums) > 10:
                    await matcher.send("每个属性不能超过10，请重新发送")
                    continue
                return nums

            elif resp == "随机":
                return random_nums()

            elif re.fullmatch(r"[\d\s]+", resp):
                await matcher.send("请发送正确的数字，如“5 5 5 5”")
                continue

            else:
                await matcher.finish("人生重开已取消")

    if random_life.result:
        nums = random_nums()
    else:
        msg = (
            "请发送4个数字分配“颜值、智力、体质、家境”4个属性，"
            "如“5 5 5 5”，或发送“随机”随机选择；"
            f"可用属性点为{total_prop}，每个属性不能超过10"
        )
        await matcher.send(msg)
        nums = await select_nums()

        if nums is None:
            await matcher.finish("人生重开已取消")

    prop = {"CHR": nums[0], "INT": nums[1], "STR": nums[2], "MNY": nums[3]}
    life.apply_property(prop)

    await matcher.send("你的人生正在重开...")

    init_prop = life.get_property()
    results = list(life.run())
    summary = life.gen_summary()

    try:
        img = await get_life_img(talents, init_prop, results, summary)
        try:
            await UniMessage.image(raw=img).send()
        except AdapterException:
            logger.warning("发送图片失败，尝试发送文件")
            await UniMessage.file(raw=img).send()
    except Exception:
        logger.warning(traceback.format_exc())
        await matcher.finish("你的人生重开失败（")


@run_sync
def get_life_img(
    talents: list[Talent],
    init_prop: PerAgeProperty,
    results: list[PerAgeResult],
    summary: Summary,
) -> BytesIO:
    return save_jpg(draw_life(talents, init_prop, results, summary))
