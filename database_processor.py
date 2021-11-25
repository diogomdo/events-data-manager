# import csv
# rows = []
# with open("open_bet_table_19092021.csv", 'r) as file:
#     csvreader = csv.reader(file)
#     header = next(csvreader)
#     for row in csvreader:
#         rows.append(row)
# print(header)
# print(rows)

import pandas as pd
import pandas_profiling as pp

data = pd.read_csv("database/open_bet_table_19092021.csv")
pp.ProfileReport(data)
