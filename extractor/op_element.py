import re
from datetime import datetime
from enum import Enum

# Constants

SEPARATOR_IDENTIFIER = "Soccer"
cached_op_results: list = []


class AssignTeamsException(Exception):
    print("Problem identifying teams name.")


class Element_Type(Enum):
    SEPARATOR = "separator"
    MATCH = "match"


class OP_Element(object):
    result: str = ""
    teams: str = ""
    date: datetime = datetime
    type: Element_Type
    main_team_name: str = ""
    opposition_name: str = ""
    page: int

    def __init__(self, element_details: [] = None, main_team: str = "", page: int = 0):
        self.eval_element_type(element_details=element_details)
        self.page = page

        if self.type is Element_Type.MATCH:
            self.date = convert_date(element_details[0])
            self.teams = element_details[1]
            self.result = extract_result(element_details[2])

            if main_team:
                self.main_team_name = main_team
                self.opposition_name = self.find_oppositor_team()

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

    def find_oppositor_team(self):
        teams = self.teams.split(" - ")
        for i, t in enumerate(teams):
            t = re.search(r"^[^(]*", t)[0].strip()
            if self.main_team_name == t or self.main_team_name in t:
                if i == 1:
                    return re.search(r"^[^(]*", teams[0])[0].strip()
                    break
                else:
                    return re.search(r"^[^(]*", teams[1])[0].strip()
                    break
            else:
                return t
                break


def extract_result(data):
    result = data.split(":")
    try:
        if result[0] == result[1]:
            return "W"
        else:
            return "L"
    except Exception:
        print("Invalid result format from data: '{}'.".format(data))
        return result


def convert_date(date: str) -> datetime:
    if "Today" in date:
        d = date.split(",")
        today = datetime.now().today().date()
        date = str(today.day) + "/" + str(today.month) + "," + d[1]
    if "Yest." in date:
        d = date.split(",")
        today = datetime.now().today().date()
        date = str(today.day - 1) + "/" + str(today.month) + "," + d[1]
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

    if event_month != 12 and not 12 in l and event_month > datetime.now().date().month:
        counter = counter + 1

    return counter
