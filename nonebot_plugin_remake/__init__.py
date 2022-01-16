import re
import random
import itertools
import traceback
from typing import List, Tuple, Union
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.params import ArgPlainText, State
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.log import logger

from .life import Life
from .talent import Talent


__help__plugin_name__ = 'remake'
__des__ = '人生重开模拟器'
__cmd__ = '''
@我 remake/liferestart/人生重开
'''.strip()
__short_cmd__ = __cmd__
__example__ = '''
@小Q remake
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


remake = on_command('remake', aliases={'liferestart', '人生重开', '人生重来'},
                    block=True, rule=to_me(), priority=11)


@remake.handle()
async def _(state: T_State = State()):
    life = Life()
    life.load()
    talents = life.rand_talents(10)
    state['life'] = life
    state['talents'] = talents
    msg = '请发送编号选择3个天赋，如“0 1 2”，或发送“随机”随机选择'
    des = '\n'.join(
        [f'{i}.{t.name}（{t.description}）' for i, t in enumerate(talents)])
    await remake.send(f"{msg}\n\n{des}")


@remake.got('nums')
async def _(reply: str = ArgPlainText('nums'), state: T_State = State()):
    def conflict_talents(talents: List[Talent]) -> Tuple[Talent, Talent]:
        for (t1, t2) in itertools.combinations(talents, 2):
            if t1.exclusive_with(t2):
                return (t1, t2)
        return None

    life: Life = state.get('life')
    talents: List[Talent] = state.get('talents')

    match = re.fullmatch(r'\s*(\d)\s*(\d)\s*(\d)\s*', reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        nums.sort()
        if nums[-1] >= 10:
            await remake.reject('请发送正确的编号')

        talents_selected = [talents[n] for n in nums]
        ts = conflict_talents(talents_selected)
        if ts:
            await remake.reject(f'你选择的天赋“{ts[0].name}”和“{ts[1].name}”不能同时拥有，请重新选择')
    elif reply == '随机':
        while True:
            nums = random.sample(range(10), 3)
            nums.sort()
            talents_selected = [talents[n] for n in nums]
            if not conflict_talents(talents_selected):
                break
    elif re.fullmatch(r'[\d\s]+', reply):
        await remake.reject('请发送正确的编号，如“0 1 2”')
    else:
        await remake.finish('人生重开已取消')

    life.set_talents(talents_selected)
    state['talents_selected'] = talents_selected

    msg = '请发送4个数字分配“颜值、智力、体质、家境”4个属性，如“5 5 5 5”，或发送“随机”随机选择；' \
        f'可用属性点为{life.total_property()}，每个属性不能超过10'
    await remake.send(msg)


@remake.got('prop')
async def _(bot: Bot, event: GroupMessageEvent,
            reply: str = ArgPlainText('prop'), state: T_State = State()):
    life: Life = state.get('life')
    talents: List[Talent] = state.get('talents_selected')
    total_prop = life.total_property()

    match = re.fullmatch(
        r'\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*', reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        if sum(nums) != total_prop:
            await remake.reject(f'属性之和需为{total_prop}，请重新发送')
        elif max(nums) > 10:
            await remake.reject('每个属性不能超过10，请重新发送')
    elif reply == '随机':
        half_prop1 = int(total_prop / 2)
        half_prop2 = total_prop - half_prop1
        num1 = random.randint(0, half_prop1)
        num2 = random.randint(0, half_prop2)
        nums = [num1, num2, half_prop1-num1, half_prop2-num2]
        random.shuffle(nums)
    elif re.fullmatch(r'[\d\s]+', reply):
        await remake.reject('请发送正确的数字，如“5 5 5 5”')
    else:
        await remake.finish('人生重开已取消')

    prop = {'CHR': nums[0], 'INT': nums[1], 'STR': nums[2], 'MNY': nums[3]}
    life.apply_property(prop)

    await remake.send('你的人生正在重开...')

    msgs = []
    msgs.append("已选择以下天赋：\n" +
                '\n'.join([f'{t.name}（{t.description}）' for t in talents]))
    msgs.append("已设置如下属性：\n" +
                f"颜值{nums[0]} 智力{nums[1]} 体质{nums[2]} 家境{nums[3]}")
    try:
        life_msgs = []
        for s in life.run():
            life_msgs.append('\n'.join(s))
        n = 5
        life_msgs = ['\n\n'.join(life_msgs[i:i + n])
                     for i in range(0, len(life_msgs), n)]
        msgs.extend(life_msgs)
        msgs.append(life.gen_summary())

        await send_forward_msg(bot, event, '人生重开模拟器', bot.self_id, msgs)
    except:
        logger.warning(traceback.format_exc())
        await remake.finish('你的人生重开失败（')


async def send_forward_msg(bot: Bot, event: GroupMessageEvent, name: str, uin: str,
                           msgs: List[Union[str, MessageSegment]]):
    def to_json(msg):
        return {
            'type': 'node',
            'data': {
                'name': name,
                'uin': uin,
                'content': msg
            }
        }
    msgs = [to_json(msg) for msg in msgs]
    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
