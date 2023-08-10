import itertools
import random
import re
import traceback
from io import BytesIO
from typing import List, Optional, Tuple

from nonebot import get_driver, on_command, require
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from nonebot.params import ArgPlainText
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.utils import run_sync

require("nonebot_plugin_saa")

from nonebot_plugin_saa import Image, MessageFactory
from nonebot_plugin_saa import __plugin_meta__ as saa_plugin_meta

from .config import Config
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
    config=Config,
    supported_adapters=saa_plugin_meta.supported_adapters,
    extra={
        "unique_name": "remake",
        "example": "@小Q remake",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.3.3",
    },
)

remake_config = Config.parse_obj(get_driver().config.dict())

onebot_v11_loaded = False
if remake_config.remake_send_forword_msg:
    try:
        from nonebot.adapters.onebot.v11 import Bot as V11Bot
        from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
        from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent

        def is_onebot_v11(bot: Bot):
            return isinstance(bot, V11Bot)

        async def send_forward_msg(
            bot: V11Bot,
            event: V11MEvent,
            name: str,
            uin: str,
            msgs: List[str],
        ):
            def to_json(msg):
                return {
                    "type": "node",
                    "data": {"name": name, "uin": uin, "content": msg},
                }

            messages = [to_json(msg) for msg in msgs]
            if isinstance(event, V11GMEvent):
                await bot.call_api(
                    "send_group_forward_msg", group_id=event.group_id, messages=messages
                )
            else:
                await bot.call_api(
                    "send_private_forward_msg", user_id=event.user_id, messages=messages
                )

        onebot_v11_loaded = True
    except ImportError:
        logger.warning("无法加载 OneBot V11 适配器，发送转发消息设置失效")


remake = on_command(
    "remake",
    aliases={"liferestart", "人生重开", "人生重来"},
    block=True,
    rule=to_me(),
    priority=12,
)


@remake.handle()
async def _(state: T_State):
    life_ = Life()
    life_.load()
    talents = life_.rand_talents(10)
    state["life"] = life_
    state["talents"] = talents
    msg = "请发送编号选择3个天赋，如“0 1 2”，或发送“随机”随机选择"
    des = "\n".join([f"{i}.{t}" for i, t in enumerate(talents)])
    await remake.send(f"{msg}\n\n{des}")


@remake.got("nums")
async def _(state: T_State, reply: str = ArgPlainText("nums")):
    def conflict_talents(talents: List[Talent]) -> Optional[Tuple[Talent, Talent]]:
        for t1, t2 in itertools.combinations(talents, 2):
            if t1.exclusive_with(t2):
                return t1, t2
        return None

    life_: Life = state["life"]
    talents: List[Talent] = state["talents"]

    match = re.fullmatch(r"\s*(\d)\s*(\d)\s*(\d)\s*", reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        nums.sort()
        if nums[-1] >= 10:
            await remake.reject("请发送正确的编号")

        talents_selected = [talents[n] for n in nums]
        ts = conflict_talents(talents_selected)
        if ts:
            await remake.reject(f"你选择的天赋“{ts[0].name}”和“{ts[1].name}”不能同时拥有，请重新选择")
    elif reply == "随机":
        while True:
            nums = random.sample(range(10), 3)
            nums.sort()
            talents_selected = [talents[n] for n in nums]
            if not conflict_talents(talents_selected):
                break
    elif re.fullmatch(r"[\d\s]+", reply):
        await remake.reject("请发送正确的编号，如“0 1 2”")
    else:
        await remake.finish("人生重开已取消")

    life_.set_talents(talents_selected)
    state["talents_selected"] = talents_selected

    msg = (
        "请发送4个数字分配“颜值、智力、体质、家境”4个属性，如“5 5 5 5”，或发送“随机”随机选择；"
        f"可用属性点为{life_.total_property()}，每个属性不能超过10"
    )
    await remake.send(msg)


@remake.got("prop")
async def _(
    bot: Bot,
    event: Event,
    state: T_State,
    reply: str = ArgPlainText("prop"),
):
    life_: Life = state["life"]
    talents: List[Talent] = state["talents_selected"]
    total_prop = life_.total_property()

    match = re.fullmatch(r"\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*", reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        if sum(nums) != total_prop:
            await remake.reject(f"属性之和需为{total_prop}，请重新发送")
        elif max(nums) > 10:
            await remake.reject("每个属性不能超过10，请重新发送")
    elif reply == "随机":
        half_prop1 = int(total_prop / 2)
        half_prop2 = total_prop - half_prop1
        num1 = random.randint(0, half_prop1)
        num2 = random.randint(0, half_prop2)
        nums = [num1, num2, half_prop1 - num1, half_prop2 - num2]
        random.shuffle(nums)
    elif re.fullmatch(r"[\d\s]+", reply):
        await remake.reject("请发送正确的数字，如“5 5 5 5”")
    else:
        await remake.finish("人生重开已取消")

    prop = {"CHR": nums[0], "INT": nums[1], "STR": nums[2], "MNY": nums[3]}
    life_.apply_property(prop)

    await remake.send("你的人生正在重开...")

    init_prop = life_.get_property()
    results = [result for result in life_.run()]
    summary = life_.gen_summary()

    try:
        if (
            remake_config.remake_send_forword_msg
            and onebot_v11_loaded
            and is_onebot_v11(bot)
        ):
            assert isinstance(bot, V11Bot)
            assert isinstance(event, V11MEvent)
            msgs = get_life_msgs(talents, init_prop, results, summary)
            await send_forward_msg(bot, event, "人生重开模拟器", bot.self_id, msgs)
            return

        img = await get_life_img(talents, init_prop, results, summary)
        await MessageFactory(Image(img)).send()
    except:
        logger.warning(traceback.format_exc())
        await remake.finish("你的人生重开失败（")


@run_sync
def get_life_img(
    talents: List[Talent],
    init_prop: PerAgeProperty,
    results: List[PerAgeResult],
    summary: Summary,
) -> BytesIO:
    return save_jpg(draw_life(talents, init_prop, results, summary))


def get_life_msgs(
    talents: List[Talent],
    init_prop: PerAgeProperty,
    results: List[PerAgeResult],
    summary: Summary,
):
    msgs = [
        "已选择以下天赋：\n" + "\n".join([str(t) for t in talents]),
        "已设置如下属性：\n"
        + f"颜值{init_prop.CHR} 智力{init_prop.INT} 体质{init_prop.STR} 家境{init_prop.MNY}",
    ]
    life_msgs = [str(result) for result in results]
    n = 5
    life_msgs = ["\n\n".join(life_msgs[i : i + n]) for i in range(0, len(life_msgs), n)]
    msgs.extend(life_msgs)
    msgs.append(str(summary))
    return msgs
