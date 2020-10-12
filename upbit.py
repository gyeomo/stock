import pyupbit
import numpy as np
import timeit
import queue
from IPython.display import clear_output
from time import sleep
from random import *
import pandas as pd
from matplotlib import pyplot as plt
import mpl_finance
import os
#시뮬레이션
current_money = 100000
current_stock = 0
data_log = []
while True :
    clear_output(wait = True)
    os.system('cls')
    os.system('clear')
    #현재 교차점이 있는지 여부 판별
    table_data = pd.DataFrame(pyupbit.get_ohlcv("KRW-EOS", interval="minute1")
                              ,columns=['open', 'high',
                                 'low', 'close', 'volume'])
    table_data['date'] = table_data.index
    table_data= table_data.reset_index()
    table_data.drop(['index'],axis='columns',inplace=True)
    rolling_5 = table_data.rolling(window=15).mean()
    rolling_20 = table_data.rolling(window=50).mean()

    intersection = 0
    turnpoint, interval = False, False
    first_track = True
    for idx in range(len(table_data.index)-2, len(table_data.index)):
        turnpoint = interval
        if rolling_5['close'].iloc[idx] - rolling_20['close'].iloc[idx] > 0:
            interval = True
        else:
            interval = False
        if first_track:
            first_track = False
            turnpoint = interval
        if interval != turnpoint:
            intersection = idx
    print("intersection : {}".format(intersection))

    #빨간선 상승여부 판별
    vals = list(rolling_5['close'].iloc[-5:len(rolling_5)])
    vals.reverse()
    inclination_red = 0
    for i in range(4):
        inclination_red += vals[i]-vals[i+1]
    print("inclination_red  : {}".format(inclination_red))
    
    vals = list(rolling_20['close'].iloc[-5:len(rolling_20)])
    vals.reverse()
    inclination_green = 0
    for i in range(4):
        inclination_green += vals[i]-vals[i+1]
    print("inclination_green  : {}".format(inclination_green))

    #매수가
    current_price = pyupbit.get_current_price("KRW-EOS")
    buy_price = current_price
    print("buy_price    : {}".format(buy_price))

    #매도가
    sell_price = buy_price+5
    print("sell_price   : {}".format(sell_price))

    #매도가(던지기)
    data = pd.DataFrame(pyupbit.get_orderbook(tickers="KRW-EOS"))
    bid_price = data.orderbook_units[0][0]['bid_price']
    print("bid_price    : {}".format(bid_price))
    
    ###시뮬레이션
    
    #매수
    if current_stock == 0:
        if inclination_red > 0.7 and inclination_green > 0.4:
            num_buy_stock  = int(current_money/(buy_price*1.0005))
            current_stock = num_buy_stock
            current_money -= (num_buy_stock*buy_price)*1.0005
            str_log = "매수1: %5.2f 주량: %5d 현재돈: %5.2f"%(buy_price,current_stock,current_money)
            data_log.append(str_log)
            print('wait...')
            sleep(80)
        elif inclination_red > 0.7 and intersection != 0:
            num_buy_stock  = int(current_money/(buy_price*1.0005))
            current_stock = num_buy_stock
            current_money -= (num_buy_stock*buy_price)*1.0005
            str_log = "매수2: %5.2f 주량: %5d 현재돈: %5.2f"%(buy_price,current_stock,current_money)
            data_log.append(str_log)
            print('wait...')
            sleep(80)
    if current_stock > 0:
        if current_stock > 0:
            #매도
            num_sell_stock  = num_buy_stock
            current_stock -= num_sell_stock
            current_money  += (num_sell_stock*sell_price)*0.9995
            str_log = "매도1: %5.2f 주량: %5d 현재돈: %5.2f"%(sell_price,current_stock,current_money)
            data_log.append(str_log)

            #던지기 - 현재 bid_price로 판매되도록 하도록 추가해야 함
            if inclination_red < 0 and intersection != 0:
                num_sell_stock  = current_stock
                current_stock -= current_stock
                current_money  += (num_sell_stock*bid_price)*0.9995
                str_log = "매도2: %5.2f 주량: %5d 현재돈: %5.2f"%(bid_price,current_stock,current_money)
                data_log.append(str_log)
        
    print("current_money  : {}".format(current_money))
    print("current_stock  : {}".format(current_stock))
    for data in data_log:
        print(data)
    if current_money <0 or current_stock<0:
        print('error')
        break
    sleep(1)
