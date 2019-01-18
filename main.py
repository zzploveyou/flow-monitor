#!/usr/bin/python3
"""
爬取路由器实时设备网速数据，记录流量消耗
路由器型号：TL-WDR7500
"""

import os
import log
import re
import sqlite3
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# global variables
PASSWORD = open("password.txt").read().strip()

START_TIME = datetime.today()
DEVICES_FILE = "devices.txt"
DBFILE = "net_flow.db"
CONN = sqlite3.connect(DBFILE)
CURSOR = CONN.cursor()
MG = log.Terminal_log(logfilename="flow-monitor.log")
if os.path.exists(DEVICES_FILE):
    # name to device_id
    DEVICES = {
        i: j
        for i, j in
        [line.strip().split("\t") for line in open(DEVICES_FILE).readlines()]
    }
else:
    DEVICES = {}

# 重建table
TABLES = [
    i[0] for i in CURSOR.execute(
        """SELECT name FROM sqlite_master WHERE type='table' ORDER BY Name""")
    .fetchall()
]
for table in DEVICES.values():
    if table not in TABLES:
        CURSOR.execute(
            f"""CREATE TABLE {table} (date TEXT, time TEXT, up FLOAT, down FLOAT)"""
        )


def speed_float(up):
    """
    10KB/s -> 10,
    1MB/s -> 1024
    >>> speed_float("10KB/s")
    10.0
    >>> speed_float("1MB/s")
    1024.0
    """
    number = float(re.search("\d+", up).group())
    if "MB" in up:
        number *= 1024
    return number


def save_record(date, time, name, up, down):
    global DEVICES, DEVICES_FILE, MG, CURSOR
    # 未产生流量则不保存
    if re.search("\d+", up).group() == '0' and re.search("\d+",
                                                         down).group() == '0':
        return
    # 名称简单处理
    name = name.replace("（本机）", "").strip()
    table_name = ""
    if name in DEVICES:
        table_name = DEVICES[name]
    else:
        # 新设备编号登记
        for i in range(1000):
            if f"device{i:03d}" not in DEVICES.values():
                table_name = f"device{i:03d}"
                with open(DEVICES_FILE, 'a') as f:
                    f.write(f"{name}\t{table_name}\n")
                DEVICES[name] = table_name
                break
        # 新设备建表
        CURSOR.execute(
            f"""CREATE TABLE {table_name} (date TEXT, time TEXT, up FLOAT, down FLOAT)"""
        )
    # change flow speed to float variable(KB/s)
    up = speed_float(up)
    down = speed_float(down)
    # 上行或下载速度超过50KB/S则保存到数据库
    if up > 50 or down > 50:
        MG.debug(f"{date} {time} {table_name}:{name} {up} {down}")
        sql = f"""INSERT INTO {table_name}(date,time,up,down) VALUES('{date}', '{time}', '{up}', '{down}')"""
        CURSOR.execute(sql)


def device_flow(driver):
    global MG, START_TIME
    # 出错或每隔15min则关闭driver，并重新挂起driver
    try:
        driver.find_element_by_id("eptMngList")
        assert (datetime.today() - START_TIME).seconds < 15 * 60
    except AssertionError:
        MG.info("Restart driver regularly.")
        driver.quit()
        START_TIME = datetime.today()
        main()
    except Exception as e:
        MG.error(f"{e}")
        driver.quit()
        main()
    try:
        res = re.findall(r'''title="(.*?)".*?上行(.*?)<.*?下行(.*?)<''',
                         driver.page_source, re.S)
        for name, up, down in res:
            date = datetime.strftime(datetime.today(), '%Y-%m-%d')
            time = datetime.strftime(datetime.today(), '%H:%M:%S')
            save_record(date, time, name, up, down)
    except Exception as e:
        print(e)
        # 偶尔正在刷新中，获取当前网速失败
        sleep(0.1)


def get_device_flow(driver):
    global CONN
    while True:
        try:
            sleep(1)
            device_flow(driver)
            CONN.commit()
        except KeyboardInterrupt:
            CONN.commit()
            CONN.close()
            driver.quit()


def main():
    global MG
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--safe-mode")
    driver = webdriver.Firefox(
        firefox_options=options,
        executable_path="/usr/bin/geckodriver",
        log_path="/dev/null")

    url = "http://1.0.0.1/"
    driver.get(url)

    MG.info("trying to login ...")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'lgPwd')))
    # locate input windows
    password = driver.find_element_by_id("lgPwd")
    # click and input password
    password.click()
    password.send_keys(PASSWORD)
    driver.find_element_by_id("loginSub").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'routeMgtMbtn')))
    driver.find_element_by_id("routeMgtMbtn").click()
    MG.done("login success and start flow-monitor.")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'eptCon')))
    get_device_flow(driver)


if __name__ == '__main__':
    main()
