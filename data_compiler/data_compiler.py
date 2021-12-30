import csv
import os
import uuid
from pathlib import Path
import datetime
from datetime import datetime

now = datetime.now()
path = "../data/events/10"
COMPILED_DATA_PATH = "compiled_data"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%d-%m-%Y"
COMPILED_DATA_EXTENSION = ".csv"
DATE_TIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT
files = list(Path(path).rglob("*.[tT][xX][tT]"))
processed_teams, processed_games, processed_odds = [], [], []
loaded_teams, loaded_games, loaded_odds = [], [], []
selected_events_files = [file_name for file_name in files if "sel" in file_name.name]
events_files = [file_name for file_name in files if "sel" not in file_name.name]
print(events_files)


class Team:
    def __init__(self, name='', backed_up_data=None):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = now
        if backed_up_data:
            self.backed_up(backed_up_data.split(";"))

    def __repr__(self):
        return 'Team id: %r, name: %r, created at: %r' % (
            self.id, self.name, self.created_at.strftime(DATE_TIME_FORMAT))

    def __eq__(self, other):
        return self.name == other

    def row(self):
        return list(self.__dict__.values())

    def backed_up(self, data):
        self.id = data[0]
        self.name = data[1]
        self.created_at = datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S.%f")
        loaded_teams.append(self)


def extract_time(game_time: str):
    try:
        return datetime.strptime(game_time, '%H:%M').time()
    except ValueError:
        print("Something is wrong with time format: %r" % game_time)
        return "XX:XX"


class Game:
    def __init__(self, game_time='', game_date='', team_a_id='', team_b_id='', result='', backed_up_data=None):
        self.id = uuid.uuid4().hex
        self.game_time = extract_time(game_time=game_time)
        self.game_date = '' if not game_date else datetime.strptime(game_date, DATE_FORMAT).date()
        self.team_a_id = team_a_id
        self.team_b_id = team_b_id
        self.result = result
        self.created_at = now
        if backed_up_data:
            self.backed_up(backed_up_data.split(";"))

    def __repr__(self):
        return 'Game id: %r, Date: %r-%r, Team A: %r, Team B: %r, result: %r, create at: %r' % (self.id,
                                                                                                self.game_time,
                                                                                                self.game_date,
                                                                                                self.team_a_id,
                                                                                                self.team_b_id,
                                                                                                self.result,
                                                                                                self.created_at.strftime(
                                                                                                    DATE_TIME_FORMAT))

    def row(self):
        return list(self.__dict__.values())

    def compare_game(self, some_game):
        print(self)
        print(some_game)
        return self.game_date == some_game.game_date and \
               self.team_a_id == some_game.team_a_id and \
               self.team_b_id == some_game.team_b_id

    def backed_up(self, data):
        self.id = data[0]
        self.game_time = datetime.strptime(data[1], TIME_FORMAT).time()
        self.game_date = datetime.strptime(data[2], "%Y-%m-%d").date()
        self.team_a_id = data[3]
        self.team_b_id = data[4]
        self.result = data[5]
        self.created_at = datetime.strptime(data[6], "%Y-%m-%d %H:%M:%S.%f")
        loaded_games.append(self)


class Odd:
    def __init__(self, game_uuid='', team_a_odd='', team_draw='', team_b_odd='', factor='', odd_time='', odd_date='',
                 backed_up_data=None):
        self.game_uuid = game_uuid
        if team_a_odd:
            self.team_a_odd = float(team_a_odd.replace(",", "."))
        else:
            self.team_a_odd = 0.0
        if team_draw:
            self.team_draw = float(team_draw.replace(",", "."))
        else:
            self.team_draw = 0.0
        if team_b_odd:
            self.team_b_odd = float(team_b_odd.replace(",", "."))
        else:
            self.team_b_odd = 0.0
        if factor and any(i.isdigit() for i in factor):
            self.factor = float(factor.replace(",", "."))
        else:
            self.factor = 0.0
        self.registered_time = self.registered_time(odd_time)
        self.registered_date = self.registered_date(odd_date)
        self.created_at = now
        if backed_up_data:
            self.backed_up(backed_up_data.split(";"))

    def __repr__(self):
        return 'Time: %r:%r, Game id: %r, Odds: %r-%r-%r, Factor: %r, created at: %r' % (self.registered_time,
                                                                                         self.registered_date,
                                                                                         self.game_uuid,
                                                                                         self.team_a_odd,
                                                                                         self.team_draw,
                                                                                         self.team_b_odd,
                                                                                         self.factor,
                                                                                         self.created_at.strftime(
                                                                                             DATE_TIME_FORMAT))

    def registered_time(self, time):
        if time == '':
            return ''
        else:
            return datetime.strptime(":".join(time.split("-")[2].split(".")[0].split("_")[1:-1]), TIME_FORMAT).time()

    def registered_date(self, odd_date):
        if odd_date == '':
            return ''
        else:
            return odd_date.split("_")[0].split("/")[-1]

    def row(self):
        return list(self.__dict__.values())

    def compare_odd(self, some_odd):
        return self.game_uuid == some_odd.game_uuid and \
               self.registered_time == some_odd.registered_time and \
               self.registered_date == some_odd.registered_date

    def backed_up(self, data):
        self.game_uuid = data[0]
        self.team_a_odd = float(data[1])
        self.team_draw = float(data[2])
        self.team_b_odd = float(data[3])
        self.factor = float(data[4])
        self.registered_time = datetime.strptime(data[5], TIME_FORMAT).time()
        self.registered_date = data[6]
        self.created_at = datetime.strptime(data[7], "%Y-%m-%d %H:%M:%S.%f")
        loaded_odds.append(self)


class Event:
    def __init__(self, raw_line):
        self.game = raw_line.split(";")
        self.date = self.game[0]
        self.hour = self.game[1]
        self.odd_a = self.game[2].strip()
        self.odd_draw = self.game[3].strip()
        self.odd_b = self.game[4].strip()
        self.game_factor = self.game[6].strip()
        self.team_a = self.game[9].strip(u'\u200b')
        self.team_b = self.game[10].strip(u'\u200b')


def team_exist(team_name):
    return any(team.__eq__(team_name) for team in loaded_teams)


def get_team(some_team):
    return next((team for team in loaded_teams if team.__eq__(some_team)), None)


def validate_team(some_team):
    if not team_exist(some_team):
        team = Team(name=some_team)
        processed_teams.append(team)
        loaded_teams.append(team)
    else:
        team = get_team(some_team)
        print("%r already in teams" % team.name)
    return team.id


def teams_table(team_a, team_b):
    return validate_team(team_a), validate_team(team_b)


def game_exist(some_game):
    return next((game for game in loaded_games if game.compare_game(some_game)), None)


def games_table(start_time, start_date, team_a_id, team_b_id):
    game = Game(start_time, start_date, team_a_id, team_b_id)
    is_game = game_exist(game)
    if not is_game:
        processed_games.append(game)
        loaded_games.append(game)
        print("Game with id: %r created!" % game.id)
    else:
        game = is_game
        print("Game with id: %r already exists!" % game.id)
    return game.id


def odds_exist(some_odd):
    return next((odd for odd in loaded_odds if odd.compare_odd(some_odd)), None)


def odds_table(game_id, team_a_odd, team_draw, team_b_odd, factor, registered_time, registered_date):
    odd = Odd(game_id, team_a_odd, team_draw, team_b_odd, factor, registered_time, registered_date)
    is_odd = odds_exist(odd)
    if not is_odd:
        processed_odds.append(odd)
        loaded_odds.append(odd)
        print("Odd with id: %r created!" % odd.game_uuid)
    else:
        odd = is_odd
        print("Odd with id: %r already exists!" % odd.game_uuid)
    return odd.game_uuid


def export_to_csv_backup(collection, headers, file_title):
    with open('export/' + file_title + '-export-' + now.strftime("%d-%m-%Y_%H:%M:%S") + '.csv', 'w', encoding='UTF8',
              newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for element in collection:
            writer.writerow(element.row())


def export_events():
    export_to_csv_backup(processed_teams, teams_headers, 'teams')
    export_to_csv_backup(processed_games, game_headers, 'games')
    export_to_csv_backup(processed_odds, odds_headers, 'odds')


def load_teams(data):
    Team(backed_up_data=data)


def load_games(data):
    Game(backed_up_data=data)


def load_odds(data):
    Odd(backed_up_data=data)


def switcher(arg, data):
    switch = {
        'teams': load_teams,
        'odds': load_odds,
        'games': load_games
    }
    switch.get(arg, 'Invalid option')(data)


def update_filename_timestamp(file, output_file_path):
    return os.rename(file, COMPILED_DATA_PATH + "/" + "-".join(file.name.split("-")[:1]) + "-" + output_file_path)


def create_export_game_file(csv_files, output_file_path):
    if processed_games and not any("games" in str(csv_path) for csv_path in csv_files):
        games_csv_path = COMPILED_DATA_PATH + "/games-"
        Path(games_csv_path + output_file_path).touch(exist_ok=True)


def create_export_teams_file(csv_files, output_file_path):
    if processed_teams and not any("teams" in str(csv_path) for csv_path in csv_files):
        teams_csv_path = COMPILED_DATA_PATH + "/teams-"
        Path(teams_csv_path + output_file_path).touch(exist_ok=True)


def create_export_odds_file(csv_files, output_file_path):
    if processed_odds and not any("odds" in str(csv_path) for csv_path in csv_files):
        odds_csv_path = COMPILED_DATA_PATH + "/odds-"
        Path(odds_csv_path + output_file_path).touch(exist_ok=True)


def provision():
    output_file_path = "export-" + str(now.strftime("%d-%m-%Y_%H:%M:%S")) + COMPILED_DATA_EXTENSION
    csv_files = list(Path(COMPILED_DATA_PATH).rglob("*" + COMPILED_DATA_EXTENSION))

    create_export_game_file(csv_files, output_file_path)
    create_export_teams_file(csv_files, output_file_path)
    create_export_odds_file(csv_files, output_file_path)

    for file in list(Path(COMPILED_DATA_PATH).rglob("*" + COMPILED_DATA_EXTENSION)):
        with open(file, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            if "odd" in str(file) and processed_odds:
                for element in processed_odds:
                    print("Odd %r added!" % element)
                    writer.writerow(element.row())
                update_filename_timestamp(file, output_file_path)
            if "games" in str(file) and processed_games:
                for element in processed_games:
                    print("Game %r added!" % element)
                    writer.writerow(element.row())
                update_filename_timestamp(file, output_file_path)
            if "teams" in str(file) and processed_teams:
                for element in processed_teams:
                    print("Team %r added!" % element)
                    writer.writerow(element.row())
                update_filename_timestamp(file, output_file_path)


teams_headers = list(Team().__dict__.keys())
game_headers = list(Game().__dict__.keys())
odds_headers = list(Odd().__dict__.keys())


def load_data():
    files = list(Path(COMPILED_DATA_PATH).rglob("*" + COMPILED_DATA_EXTENSION))
    for file in files:
        with open(file, 'r', encoding='UTF-8') as f:
            while line := f.readline().rstrip():
                name = file.name.split("-")[0]
                switcher(name, line)


load_data()

for event in events_files:
    with open(event, 'r', encoding='UTF-8') as file:
        while line := file.readline().rstrip():
            event = Event(raw_line=line)
            teams_id = teams_table(event.team_a, event.team_b)
            game_id = games_table(event.hour, event.date, teams_id[0], teams_id[1])
            odds_table(game_id, event.odd_a, event.odd_draw, event.odd_b, event.game_factor, file.name, file.name)

provision()
