import sqlite3
import sys
import csv

def process_date(s):
    return s[:4]

c = sqlite3.connect(sys.argv[1])
cur = c.cursor()

reader = csv.reader(file('firstfleet.csv'))
for row in reader:
    cur.execute('insert into links values(?, ?, ?, ?, ?, ?)',
            (row[0], row[1], process_date(row[7]), '-', row[10], row[9]))
c.commit()
c.close()
