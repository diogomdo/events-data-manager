import sqlite3
from sqlite3 import Error

import pandas as pd


# conn = sqlite3.connect("database/events-data.db")
#
# df = pd.read_csv(r'compiled_data/teams-export-08-12-2021_19:14:51.csv', sep=';')
# df.to_sql('teams', conn, if_exists='append', index=False)
#
# df = pd.read_csv(r'compiled_data/games-export-08-12-2021_19:14:51.csv', sep=';')
# df.to_sql('games', con, if_exists='append', index=False)
#
# odds_ = pd.read_csv(r'compiled_data/odds-export-08-12-2021_19:14:51.csv', sep=';')
# odds_.to_sql('odds', con, if_exists='append', index=False)

PATH = "/Users/diogo.oliveira/dev/own/events-data-manager/database/events-data.db"


def create_connection():
    conn = None

    try:
        conn = sqlite3.connect(PATH)
    except Error as e:
        print(e)

    return conn


def select_all_teams():
    conn = create_connection()

    cur = conn.cursor()
    cur.execute("SELECT * FROM teams")

    rows = cur.fetchall()
    for row in rows:
        print(row)


def select_games_from_team(team_id):
    conn = create_connection()

    with conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT iif(home_team != ?, home_team, visitor_team) as opponent_id, "
            "(select team_name FROM teams WHERE teams.id = iif(home_team != ?, home_team, visitor_team)) AS opponent_name,"
            " g.id AS game_id, t.team_name, (select id from teams where team_name = t.team_name) ,g.game_date,"
            " g.game_time FROM games g JOIN teams t ON g.home_team = t.id OR"
            " g.visitor_team = t.id WHERE t.id = ? AND g.result ISNULL",
            [team_id, team_id, team_id])

        rows = cur.fetchall()

        matches_list = []
        if rows:
            for row in rows:
                matches_list.append(
                    {"opponent_id": row[0],
                     "opponent_name": row[1],
                     "game_id": row[2],
                     "team_name": row[3],
                     "team_id": row[4],
                     "match_date": row[5],
                     "match_time": row[6]
                     }
                )

        print(matches_list)
        return matches_list


def insert_result_game(game_id="", result=""):
    conn = create_connection()

    with conn:
        cur = conn.cursor()
        columns = [i[1] for i in cur.execute('PRAGMA table_info(teams)')]
        if "result" not in columns:
            cur.execute("ALTER TABLE teams ADD COLUMN result TEXT")

        cur.execute("UPDATE games SET result = ? WHERE id = ?", (result, game_id))
        conn.commit()


def insert_op_name(op_team_name="", team_id=""):
    conn = create_connection()

    with conn:
        cur = conn.cursor()
        columns = [i[1] for i in cur.execute('PRAGMA table_info(teams)')]
        if "op_team_name" not in columns:
            cur.execute("ALTER TABLE teams ADD COLUMN op_team_name TEXT")

        cur.execute("UPDATE teams SET op_team_name = ? WHERE id = ?", (op_team_name, team_id))
        conn.commit()


def insert_op_id(op_id="", team_id=""):
    conn = create_connection()

    with conn:
        cur = conn.cursor()
        columns = [i[1] for i in cur.execute('PRAGMA table_info(teams)')]
        if "op_id" not in columns:
            cur.execute("ALTER TABLE teams ADD COLUMN op_id TEXT")

        cur.execute("UPDATE teams SET op_id = ? WHERE id = ?", (op_id, team_id))
        conn.commit()


def get_op_team_name(team_id=""):
    conn = create_connection()

    with conn:
        cur = conn.cursor()

        result = cur.execute("SELECT op_team_name FROM teams WHERE id = ?", (team_id,)).fetchone()
        return result[0] if result is not None else False


def get_op_id(team_id=""):
    conn = create_connection()

    with conn:
        cur = conn.cursor()

        result = cur.execute("SELECT op_id FROM teams WHERE id = ?", (team_id,)).fetchone()
        return result[0] if result is not None else False


def get_teams_with_games():
    conn = create_connection()

    with conn:
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT home_team from games where result IS NULL ORDER BY home_team")
        result = cur.fetchall()
        return result if result is not None else False
