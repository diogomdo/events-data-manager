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

def extract_row_details(r):
    return [item.text for item in r.find_elements_by_xpath(".//*[self::td or self::th]")]
