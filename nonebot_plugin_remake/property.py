from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Set


class PropGrade(NamedTuple):
    min: int
    judge: str
    grade: int


@dataclass
class PropSummary:
    value: int

    @property
    def name(self) -> str:
        raise NotImplementedError

    def grades(self) -> List[PropGrade]:
        raise NotImplementedError

    @property
    def prop_grade(self) -> PropGrade:
        for grade in reversed(self.grades()):
            if self.value >= grade.min:
                return grade
        return self.grades()[0]

    @property
    def judge(self) -> str:
        return self.prop_grade.judge

    @property
    def grade(self) -> int:
        return self.prop_grade.grade

    def __str__(self) -> str:
        return f"{self.name}: {self.value} ({self.judge})"


class CHRSummary(PropSummary):
    @property
    def name(self) -> str:
        return "颜值"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "地狱", 0),
            PropGrade(1, "折磨", 0),
            PropGrade(2, "不佳", 0),
            PropGrade(4, "普通", 0),
            PropGrade(7, "优秀", 1),
            PropGrade(9, "罕见", 2),
            PropGrade(11, "逆天", 3),
        ]


class INTSummary(PropSummary):
    @property
    def name(self) -> str:
        return "智力"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "地狱", 0),
            PropGrade(1, "折磨", 0),
            PropGrade(2, "不佳", 0),
            PropGrade(4, "普通", 0),
            PropGrade(7, "优秀", 1),
            PropGrade(9, "罕见", 2),
            PropGrade(11, "逆天", 3),
            PropGrade(21, "识海", 3),
            PropGrade(131, "元神", 3),
            PropGrade(501, "仙魂", 3),
        ]


class STRSummary(PropSummary):
    @property
    def name(self) -> str:
        return "体质"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "地狱", 0),
            PropGrade(1, "折磨", 0),
            PropGrade(2, "不佳", 0),
            PropGrade(4, "普通", 0),
            PropGrade(7, "优秀", 1),
            PropGrade(9, "罕见", 2),
            PropGrade(11, "逆天", 3),
            PropGrade(21, "凝气", 3),
            PropGrade(101, "筑基", 3),
            PropGrade(401, "金丹", 3),
            PropGrade(1001, "元婴", 3),
            PropGrade(2001, "仙体", 3),
        ]


class MNYSummary(PropSummary):
    @property
    def name(self) -> str:
        return "家境"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "地狱", 0),
            PropGrade(1, "折磨", 0),
            PropGrade(2, "不佳", 0),
            PropGrade(4, "普通", 0),
            PropGrade(7, "优秀", 1),
            PropGrade(9, "罕见", 2),
            PropGrade(11, "逆天", 3),
        ]


class SPRSummary(PropSummary):
    @property
    def name(self) -> str:
        return "快乐"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "地狱", 0),
            PropGrade(1, "折磨", 0),
            PropGrade(2, "不幸", 0),
            PropGrade(4, "普通", 0),
            PropGrade(7, "幸福", 1),
            PropGrade(9, "极乐", 2),
            PropGrade(11, "天命", 3),
        ]


class AGESummary(PropSummary):
    @property
    def name(self) -> str:
        return "享年"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "胎死腹中", 0),
            PropGrade(1, "早夭", 0),
            PropGrade(10, "少年", 0),
            PropGrade(18, "盛年", 0),
            PropGrade(40, "中年", 0),
            PropGrade(60, "花甲", 1),
            PropGrade(70, "古稀", 1),
            PropGrade(80, "杖朝", 2),
            PropGrade(90, "南山", 2),
            PropGrade(95, "不老", 3),
            PropGrade(100, "修仙", 3),
            PropGrade(500, "仙寿", 3),
        ]


class SUMSummary(PropSummary):
    @property
    def name(self) -> str:
        return "总评"

    def grades(self) -> List[PropGrade]:
        return [
            PropGrade(0, "地狱", 0),
            PropGrade(41, "折磨", 0),
            PropGrade(50, "不佳", 0),
            PropGrade(60, "普通", 0),
            PropGrade(80, "优秀", 1),
            PropGrade(100, "罕见", 2),
            PropGrade(110, "逆天", 3),
            PropGrade(120, "传说", 3),
        ]


@dataclass
class Summary:
    CHR: CHRSummary  # 颜值
    INT: INTSummary  # 智力
    STR: STRSummary  # 体质
    MNY: MNYSummary  # 家境
    SPR: SPRSummary  # 快乐
    AGE: AGESummary  # 享年
    SUM: SUMSummary  # 总评

    def __str__(self) -> str:
        return "==人生总结==\n\n" + "\n".join(
            [
                str(self.CHR),
                str(self.INT),
                str(self.STR),
                str(self.MNY),
                str(self.SPR),
                str(self.AGE),
                str(self.SUM),
            ]
        )


class Property:
    def __init__(self):
        self.AGE: int = -1  # 年龄 age AGE
        self.CHR: int = 0  # 颜值 charm CHR
        self.INT: int = 0  # 智力 intelligence INT
        self.STR: int = 0  # 体质 strength STR
        self.MNY: int = 0  # 家境 money MNY
        self.SPR: int = 5  # 快乐 spirit SPR
        self.LIF: int = 1  # 生命 life LIFE
        self.TMS: int = 1  # 次数 times TMS
        self.TLT: Set[int] = set()  # 天赋 talent TLT
        self.EVT: Set[int] = set()  # 事件 event EVT
        self.AVT: Set[int] = set()  # 触发过的事件 Achieve Event
        self.total: int = 20

    def apply(self, effect: Dict[str, int]):
        for key in effect:
            if key == "RDM":
                k = ["CHR", "INT", "STR", "MNY", "SPR"][id(key) % 5]
                setattr(self, k, getattr(self, k) + effect[key])
                continue
            setattr(self, key, getattr(self, key) + effect[key])

    def gen_summary(self) -> Summary:
        self.SUM = (
            self.CHR + self.INT + self.STR + self.MNY + self.SPR
        ) * 2 + self.AGE // 2
        return Summary(
            CHR=CHRSummary(self.CHR),
            INT=INTSummary(self.INT),
            STR=STRSummary(self.STR),
            MNY=MNYSummary(self.MNY),
            SPR=SPRSummary(self.SPR),
            AGE=AGESummary(self.AGE),
            SUM=SUMSummary(self.SUM),
        )
