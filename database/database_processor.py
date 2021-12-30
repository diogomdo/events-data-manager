# import csv
# rows = []
# with open("open_bet_table_19092021.csv", 'r) as file:
#     csvreader = csv.reader(file)
#     header = next(csvreader)
#     for row in csvreader:
#         rows.append(row)
# print(header)
# print(rows)
import sqlite3
from sqlite3 import Error

import pandas as pd
import pandas_profiling as pp

data = pd.read_csv("../data/open_bet_table_19092021.csv")
pp.ProfileReport(data)

PATH = ".../database/events-data.db"


def create_connection():
    conn = None

    try:
        conn = sqlite3.connect(PATH)
    except Error as e:
        print(e)

    return conn


