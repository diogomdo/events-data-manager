from datetime import datetime
from enum import Enum

# Constants

SEPARATOR_IDENTIFIER = "Soccer"
cached_op_results: list = []


class Element_Type(Enum):
    SEPARATOR = "separator"
    MATCH = "match"


class OP_Element(object):
    result: str = ""
    teams: list = []
    date: datetime = datetime
    type: Element_Type
    page: int

    def __init__(self, element_details: [] = None, page: int = 0):
        self.eval_element_type(element_details=element_details)
        self.page = page

        if self.type is Element_Type.MATCH:
            self.date = convert_date(element_details[0])
            self.teams = element_details[1]
            self.result = element_details[2]

    def eval_element_type(self, element_details):
        if SEPARATOR_IDENTIFIER in element_details[0]:
            self.type = Element_Type.SEPARATOR
        else:
            self.type = Element_Type.MATCH

    def __eq__(self, other):
        if not isinstance(other, OP_Element):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.date == other.date and self.teams == other.teams


def convert_date(date: str) -> datetime:
    date = datetime.strptime(date, "%d/%m, %H:%M")
    year = find_year(date)
    return date.replace(year=year)


def find_year(day_month: datetime) -> int:
    current_date: datetime = datetime.now()
    year: int = current_date.year

    passed_years = count_month_occurrences(event_month=day_month.month)
    return year - passed_years


def filter_matches():
    return [x.date.month for x in cached_op_results if x.date.month]


def count_month_occurrences(event_month: int):
    l: list = [0] + filter_matches()
    counter: int = 0

    for i, month in enumerate(l):
        if month == 12 and l[i - 1] != 12:
            counter = counter + 1

    if event_month == 12 and l[-1] != 12:
        counter = counter + 1

    return counter
