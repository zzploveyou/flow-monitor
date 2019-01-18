"""
1. extract total-flow for each date of each device.
2. Remove date before.

"""
import sqlite3
import os
from datetime import datetime

DBFILE = "net_flow.db"
# global variables
RESULT_DIR = "flow"
CONN = sqlite3.connect(DBFILE)
CURSOR = CONN.cursor()
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)
DEVICES_FILE = "devices.txt"
if os.path.exists(DEVICES_FILE):
    # name to device_id
    DEVICES_NAME = {
        j: i
        for i, j in
        [line.strip().split("\t") for line in open(DEVICES_FILE).readlines()]
    }
else:
    DEVICES_NAME = {}



def cal_flow(name, date, write=True):
    res = CURSOR.execute(
        f"""SELECT time, up, down FROM {name} WHERE date='{date}'""").fetchall(
        )
    last_time = datetime.strptime(res[0][0], "%H:%M:%S")
    total_up, total_down = 0, 0
    for time, up, down in res:
        now_time = datetime.strptime(time, "%H:%M:%S")
        seconds = (now_time - last_time).seconds
        if seconds <= 10:
            """避免中断数据造成错误计算,连续10s内进入计算"""
            total_up += seconds * up
            total_down += seconds * down
        last_time = now_time
    if write:
        with open(os.path.join(RESULT_DIR, f"{DEVICES_NAME[name]}.csv"), 'a', newline="") as f:
            f.write(f"{date},{total_up/1024:.0f}M,{total_down/1024:.0f}M\n")
    print(f">>> {DEVICES_NAME[name]} >>> {date},{total_up/1024:.1f}M,{total_down/1024:.1f}M")


def collect_one_table(table):
    dates = set([
        i[0]
        for i in CURSOR.execute(f"""SELECT date FROM {table}""").fetchall()
    ])
    today = datetime.strftime(datetime.today(), '%Y-%m-%d')
    for date in dates:
        if date != today:
            cal_flow(table, date)
            CURSOR.execute(f"""DELETE FROM {table} WHERE date='{date}'""")
            CONN.commit()
        else:
            cal_flow(table, date, write=False)


def collect():
    tables = [
        i[0] for i in CURSOR.execute(
            """SELECT name FROM sqlite_master WHERE type='table' ORDER BY Name"""
        ).fetchall()
    ]

    for table in tables:
        collect_one_table(table)
    CONN.commit()
    CONN.close()


if __name__ == '__main__':
    collect()
