# -*- coding: utf-8 -*-
import os

__author__ = 'Sergey Smirnov <smirnoffs@gmail.com>'

FORECAST_API_KEY = os.getenv("FORECAST_API_KEY")
URL_MASK = 'https://api.forecast.io/forecast/{key}/{lat},{lon},{time}?units=si'
KYIV = (50.432323, 30.533685)
KHERSON = (46.631992, 32.581704)
CPH = (55.680756, 12.580061)
TZ = '+0200'


DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sql')
