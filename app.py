import streamlit as st

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU

from dateutil import parser
from dateutil.relativedelta import relativedelta
import datetime

from yahoo_fin import stock_info as si

# VIX daily prices
vix = pd.read_csv("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")

# find last weekday and add it if it's not in there
_today = datetime.datetime.today()
#if _today.weekday() > 0: # Saturday, Sunday
_today -= datetime.timedelta(1)
while (_today.weekday() > 4):
  _today -= datetime.timedelta(1)
_today_date = _today.strftime("%m/%d/%Y")
if vix.loc[len(vix)-1]['DATE'] != _today_date:
  _data = si.get_data("^VIX", start_date = _today_date)
  vix.loc[len(vix)]=[_today_date,_data['open'][0],_data['high'][0],_data['low'][0],_data['close'][0]]

# the main futures are dated the 3rd Wednesday of the month
every_3rd_wednesday = [str(x).split(" ")[0] for x in pd.date_range('2022-01-01','2023-02-28',freq='WOM-3WED')]

# read in futures data
vix_futures = {}
for x in every_3rd_wednesday:
    if x == "2022-03-16":
        x = "2022-03-15" # no clue why this was a Tuesday instead
    date = parser.parse(x)
    vix_futures[date] = pd.read_csv(f"https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{x}.csv")

BACKLOG = 2 * 30 # look at the last 60 trading days (12 weeks)

dates = np.array([parser.parse(x) for x in vix[-BACKLOG:]['DATE']])
midspot = np.array(vix[-BACKLOG:]['OPEN'] + vix[-BACKLOG:]['CLOSE']) / 2.

lo, hi = np.quantile(midspot, [0.2, 0.8])

start_date = dates[0].strftime("%d/%m/%Y")
end_date = dates[-1].strftime("%d/%m/%Y")

def get_quantiles(i, lo_q=0.2, hi_q=0.8, lookback=BACKLOG):
  mm = np.array(vix[i-lookback:i]['OPEN'] + vix[i-lookback:i]['CLOSE']) / 2.
  l, h = np.quantile(mm, [lo_q, hi_q])
  return l, h

st.title("VIX")

lo_30, hi_30 = get_quantiles(len(vix), lookback=30)
lo_45, hi_45 = get_quantiles(len(vix), lookback=45)
lo_60, hi_60 = get_quantiles(len(vix), lookback=60)

cur_datee = dates[-1].strftime("%d %B %A")
st.text(f"Data including {cur_datee}.\n30 days upper 20% = {hi_30:.2f}, lower 20% = {lo_30:.2f}\n45 days upper 20% = {hi_45:.2f}, lower 20% = {lo_45:.2f}\n60 days upper 20% = {hi_60:.2f}, lower 20% = {lo_60:.2f}")