import sqlite3
import sys
import csv

import re

def process_date(s):
    results = re.findall(r'\d{4}', s)
    if results: return results[-1]
    return None

c = sqlite3.connect(sys.argv[1])
cur = c.cursor()

reader = csv.reader(file('sydney1955.csv'))
for row in reader:
    cur.execute('insert into links values(?, ?, ?, ?, ?, ?)',
            (row[0], row[1], process_date(row[4]), '-', row[9], row[8]))
c.commit()
c.close()
