from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List

from .age import AgeManager
from .event import EventManager
from .property import Property, Summary
from .talent import Talent, TalentManager

data_path = Path(__file__).parent / "resources" / "data"


@dataclass
class PerAgeProperty:
    AGE: int  # 年龄
    CHR: int  # 颜值
    INT: int  # 智力
    STR: int  # 体质
    MNY: int  # 家境
    SPR: int  # 快乐

    def __str__(self) -> str:
        return (
            f"【{self.AGE}岁/颜{self.CHR}智{self.INT}"
            f"体{self.STR}钱{self.MNY}乐{self.SPR}】"
        )


@dataclass
class PerAgeResult:
    property: PerAgeProperty
    event_log: List[str]
    talent_log: List[str]

    def __str__(self) -> str:
        return (
            f"{self.property}\n"
            + "\n".join(self.event_log)
            + "\n".join(self.talent_log)
        )


class Life:
    def __init__(self):
        self.property = Property()
        self.age = AgeManager(self.property)
        self.event = EventManager(self.property)
        self.talent = TalentManager(self.property)

    def load(self):
        self.age.load(data_path / "age.json")
        self.event.load(data_path / "events.json")
        self.talent.load(data_path / "talents.json")

    def alive(self) -> bool:
        return self.property.LIF > 0

    def get_property(self) -> PerAgeProperty:
        return PerAgeProperty(
            self.property.AGE,
            self.property.CHR,
            self.property.INT,
            self.property.STR,
            self.property.MNY,
            self.property.SPR,
        )

    def run(self) -> Iterator[PerAgeResult]:
        while self.alive():
            self.age.grow()
            talent_log = self.talent.update_talent()
            event_log = self.event.run_events(self.age.get_events())
            yield PerAgeResult(
                self.get_property(),
                list(event_log),
                list(talent_log),
            )

    def rand_talents(self, num: int) -> List[Talent]:
        return list(self.talent.rand_talents(num))

    def set_talents(self, talents: List[Talent]):
        for t in talents:
            self.talent.add_talent(t)
        self.talent.update_talent_prop()

    def apply_property(self, effect: Dict[str, int]):
        self.property.apply(effect)

    def total_property(self) -> int:
        return self.property.total

    def gen_summary(self) -> Summary:
        return self.property.gen_summary()
