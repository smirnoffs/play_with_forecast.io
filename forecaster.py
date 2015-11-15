# -*- coding: utf-8 -*-
from settings import KYIV, TZ, URL_MASK, FORECAST_API_KEY, DB, KHERSON, CPH

__author__ = 'Sergey Smirnov <smirnoffs@gmail.com>'

from datetime import datetime, timedelta
import sqlite3
import json
import requests

connection = sqlite3.connect(DB)
cursor = connection.cursor()


def _prepare_time(time=datetime.now(), tz_add=True):
    iso_time = time.isoformat().split('.')[0]
    if tz_add:
        return iso_time + TZ
    return iso_time


def _join_coords(coords):
    return ','.join(str(c) for c in coords)


def get_forecast(coords=KYIV, time=_prepare_time()):
    lat, lon = coords
    url = URL_MASK.format(key=FORECAST_API_KEY, lat=lat, lon=lon, time=time)
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.content, coords, time


def save_to_database(data, coords, time):
    coords = _join_coords(coords)
    time = time.split('+')[0]
    insert_sql = "INSERT INTO results VALUES ('{time}', '{coords}', '{data}')".format(time=time,
                                                                                      coords=coords,
                                                                                      data=data.decode('utf-8'))
    cursor.execute(insert_sql)
    connection.commit()


def get_current_temperature(data):
    return data['currently']['temperature']


def load_forecast(coords=KYIV, time=_prepare_time()):
    result = get_forecast(coords=coords, time=time)
    if result:
        save_to_database(*result)
        return True


def _get_temperature_from_row(rowid):
    cursor.execute("SELECT result from results where ROWID={0}".format(rowid))
    data = json.loads(cursor.fetchone()[0])
    return get_current_temperature(data)


def get_last_forecast(coords=KYIV):
    select_sql = "SELECT ROWID, time FROM results WHERE coords='{coords}' and time > '{last_hour}'" \
                 "ORDER BY time LIMIT 1".format(coords=_join_coords(coords),
                                                last_hour=_prepare_time(datetime.now() - timedelta(hours=1),
                                                                        tz_add=False))
    cursor.execute(select_sql)
    result = cursor.fetchone()
    if result:
        rowid = result[0]
        return _get_temperature_from_row(rowid)
    else:
        if load_forecast(coords):
            return get_last_forecast(coords)


def get_yesterday_forecast(coords):
    start = _prepare_time(datetime.now() - timedelta(days=1, minutes=30), tz_add=False)
    end = _prepare_time(datetime.now() - timedelta(days=1, minutes=-30), tz_add=False)
    sql = "SELECT ROWID from results WHERE coords='{coords}' and time BETWEEN '{start}' AND '{end}'".format(
        coords=_join_coords(coords),
        start=start,
        end=end)
    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        rowid = result[0]
        return _get_temperature_from_row(rowid)
    else:
        load_forecast(coords=coords, time=_prepare_time(datetime.now() - timedelta(days=1)))
        return get_yesterday_forecast(coords)


def compare_weather(coords):
    data = dict(yesterday=get_yesterday_forecast(coords), today=get_last_forecast(coords))
    frmt_string = '{compare_result} today. Now {today}\N{DEGREE SIGN}C, yesterday was {yesterday}\N{DEGREE SIGN}C'
    if data['today'] < data['yesterday']:
        result = frmt_string.format(compare_result='Colder', **data)
    else:
        result = frmt_string.format(compare_result='Warmer', **data)
    return result


if __name__ == '__main__':
    # load_forecast(KHERSON)
    coords = CPH
    print(compare_weather(coords))
