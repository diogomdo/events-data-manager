# import pandas as pd


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
import logging
import unicodedata
from itertools import combinations


def extract_row_details(r):
    return [item.text.strip() for item in r.find_elements_by_xpath(".//*[self::td or self::th]")]


def get_combination_list(team_name: str) -> list:
    logging.info("Compiling number of combinations for team '{}'.".format(team_name))
    n = team_name.split()
    compiled_list = sum([list(map(list, combinations(n, i))) for i in range(len(n) + 1)], [])

    # TODO remove empty result from compiled list
    # TODO join() any result with len > 1
    # TODO discard any result with len == 1 and size <= 3
    logging.info("Total combinations: {}".format(compiled_list))
    return compiled_list


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')
