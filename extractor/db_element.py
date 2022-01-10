from datetime import datetime


class DB_Element(object):
    game_id: str = ""
    opponent_id: str = ""
    opponent_name: str = ""
    main_team_id: str = ""
    main_team_name: str = ""
    match_date_time: datetime = None

    def __init__(self, db_data):
        self.game_id = db_data[2]
        self.opponent_id = db_data[0]
        self.opponent_name = db_data[1]
        self.main_team_id = db_data[4]
        self.main_team_name = db_data[3]
        self.match_date_time = datetime.strptime(", ".join([db_data[5], db_data[6]]), "%Y-%m-%d, %H:%M:%S")
