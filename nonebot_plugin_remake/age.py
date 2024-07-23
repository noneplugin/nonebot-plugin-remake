import json
from pathlib import Path

from .event import WeightedEvent
from .property import Property


class AgeManager:
    def __init__(self, prop: Property):
        self.prop = prop
        self.ages: dict[int, list[WeightedEvent]] = {}

    def load(self, path: Path):
        data: dict[str, dict] = json.load(path.open("r", encoding="utf8"))
        self.ages = {
            int(k): [WeightedEvent(s) for s in v.get("event", [])]
            for k, v in data.items()
        }

    def get_events(self) -> list[WeightedEvent]:
        return self.ages[self.prop.AGE]

    def grow(self):
        self.prop.AGE += 1
