import re
from typing import List

from nonebot.log import logger


class DummyList(list):
    def __init__(self, lst: List[int]):
        super().__init__(lst)

    def __contains__(self, obj: object) -> bool:
        if isinstance(0, set):
            for x in self:
                if x in obj:
                    return True
            return False
        return super().__contains__(obj)


def parse_condition(cond: str):
    reg_attr = re.compile("[A-Z]{3}")
    cond2 = (
        reg_attr.sub(
            lambda m: f'getattr(x, "{m.group()}")', cond.replace("AEVT", "AVT")
        )
        .replace("?[", " in DummyList([")
        .replace("![", "not in DummyList([")
        .replace("]", "])")
        .replace("|", " or ")
    )
    while True:
        try:
            func = eval(f"lambda x: {cond2}")
            func.__doc__ = cond2
            return func
        except Exception:
            logger.warning(f"[WARNING] missing ) in {cond}")
            cond2 += ")"
