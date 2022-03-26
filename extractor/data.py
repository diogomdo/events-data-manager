import logging
import sqlite3
from sqlite3 import Error

from extractor.db_element import DB_Element
from model.team_db import Team_db

PATH = "/Users/diogo.oliveira/dev/own/events-data-manager/database/events-data.db"
"""
TODO:
- Remove duplicate entries from teams table.
- Verify what is auto inserting result column in teams table.
- Add to retrieve matches without result query, the condition where `result` is null, the is empty clause.
"""


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


def get_teams_without_alias():
    conn = create_connection()

    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE op_id is NULL or op_id is NULL")

    rows = cur.fetchall()
    logging.info("Total teams with missing alias: {}".format(len(rows)))
    matches_list = []
    if rows:
        for row in rows:
            matches_list.append(Team_db(db_data=row))

    return matches_list


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
                matches_list.append(DB_Element(db_data=row))

        # print(matches_list)
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


def insert_op_quick_link(team_id="", op_id=""):
    conn = create_connection()

    with conn:
        cur = conn.cursor()
        columns = [i[1] for i in cur.execute('PRAGMA table_info(teams)')]
        if "op_id" not in columns:
            cur.execute("ALTER TABLE teams ADD COLUMN op_id TEXT")

        cur.execute("UPDATE teams SET op_id = ? WHERE id = ?", (op_id, team_id))
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


def delete_duplicate_entries():
    conn = create_connection()

    with conn:
        cur = conn.cursor()

        cur.execute("SELECT  DISTINCT rowID, COUNT(*) c FROM teams GROUP BY id HAVING c = 1;")
        result = cur.fetchall()
        print(len(result))
        for i in result:
            cur.execute("DELETE FROM teams WHERE rowid = ?", (i[0],))
