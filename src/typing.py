from typing import List


class betterDict(dict):
    def __getattr__(self, item):
        return self.get(item, None)

    def __setattr__(self, key, value):
        self[key] = value


class Lesson_Dict(betterDict):
    score: str
    type: str
    name: str
    detail_time: str
    place: str
    time: str
    lesson_index: int


class Schedule_Dict(betterDict):
    weekday: str
    lessons: List[Lesson_Dict]
