from datetime import datetime
from enum import Enum


class SubCategory(Enum):
    B = "B",
    S18 = "U18",
    S23 = "U23",
    F = "F"


class Team_db(object):
    team_id: str = ""
    team_name: str = ""
    team_alias: str = ""
    team_quick_link: str = ""
    sub_category: SubCategory = None
    created_at: datetime = None

    def __init__(self, db_data):
        self.team_id = db_data[0]
        self.team_name = db_data[1]
        self.created_at = datetime.strptime(db_data[2], "%Y-%m-%d %H:%M:%S.%f")
        self.team_alias = db_data[3]
        self.team_quick_link = db_data[4]

    def sub_category_resolver(self):
        pass
