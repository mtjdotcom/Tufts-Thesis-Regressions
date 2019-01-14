#ani = animation.FuncAnimation(fig, animate, interval = 5000) 
#plt.show()

#http://api.bitcoincharts.com/v1/trades.csv?symbol=btceUSD
#http://api.bitcoincharts.com/v1/trades.csv?symbol=btcexYAD&start=1401983000
#https://btc-e.com/api/2/btc_usd/trades  


import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import time
import sys, getopt
import json
import urllib2, urllib
from matplotlib import dates
import pandas as pd
from pandas import Series
from matplotlib.finance import candlestick
import threading
import datetime
from pylab import *
import requests


def recentHistory():
    
    url = "http://api.bitcoincharts.com/v1/trades.csv?symbol=bitfinexUSD"
    f = urllib2.urlopen(url).read()
    
    fLines = f.split("\n")
    num = []
    for lines in fLines:
        tempList = []
        date, price, volume = lines.split(",")
        date = int(date)
        historyDateAr.append(date)
        price = float(price)

        volume = float(volume)

        tempList.append(price)
        tempList.append(volume)
        num.append(tempList)
    

    reverseNum = []
    reverseHistoryDate = []
    
    for i in reversed(num):
        reverseNum.append(i)
    for i in reversed(historyDateAr):
        reverseHistoryDate.append(i)

    column = ["price", "volume"]   
    df = pd.DataFrame(reverseNum, index= reverseHistoryDate, columns = column)


    return df


def dataToCandle(timeDelta):
    
    df = recentHistory()
    openL = []
    closeL = []
    highL = []
    lowL = []
    volumeL = []
    
    
    
    start = df.index[0] - (df.index[0] % timeDelta)
    
    
    print start
    end = df.index[-1] - (df.index[-1] % timeDelta)
    
    #letzten 2 Stunden: 7200
    limit = 28800
    start = end - limit
    

    printcounter = 0
    while start < df.index[-1]:
        tempPrice = []
        tempVolume = []
        for i in range(0,timeDelta):
            coord = start + i
            
            
            printcounter +=1
            if printcounter % 10000 == 0:
                print "Currently at point:",printcounter,". Out of:",(df.index[-1]- df.index[0]) ," -- Appendings Data"
                print "-------------"
            try:
                databit =  df.loc[coord]
                priceDF = databit["price"]
                volumeDF = databit["volume"]
                try:
                    priceDF = float(priceDF)
                    tempPrice.append(priceDF)
                    volumeDF = float(volumeDF)
                    tempVolume.append(volumeDF)
            
                except:
                    for price in priceDF:
                        tempPrice.append(price)
                    for volume in volumeDF:
                        tempVolume.append(volume)
            except KeyError:
                continue
            

        try: 
            high = max(tempPrice)
            low = min(tempPrice)
            open = tempPrice[0]
            close = tempPrice[-1]
            volume = sum(tempVolume)
            dateL.append(start)
            openL.append(open)
            highL.append(high)
            lowL.append(low)
            closeL.append(close)
            volumeL.append(volume)
            start+= timeDelta
        except ValueError:
            start+= timeDelta
            continue
        
        
        
    for digit in range(len(openL)):
        date = dates.epoch2num(dateL[digit])
        appendLine =  date, openL[digit], closeL[digit], highL[digit], lowL[digit]
        candleAr.append(appendLine)  


def bid_askTicker( symbol='btcusd'):     

    URL = "https://api.bitfinex.com/v1"
    r = requests.get(URL + "/book/" + symbol, verify=False)
    currentOrderBook = r.json()
    
 
    
    bidsAr = currentOrderBook["bids"]
    askAr = currentOrderBook["asks"]

    currentBid = float(bidsAr[0]["price"])
    currentAsk = float(askAr[0]["price"])

    
    return currentBid, currentAsk

def tradeDataFeed(symbol='btcusd'):
    
    URL = "https://api.bitfinex.com/v1"
    
    r = requests.get(URL + "/ticker/" + symbol, verify=False)
    tickerData = r.json()

    try:
        tickerData['last_price']
    except KeyError:
        return tickerData['message']

    lastPrice = tickerData["last_price"]
    lastPrice = float(lastPrice)
    currentTime = tickerData["timestamp"]
    currentTime = float(currentTime)
    currentTime = currentTime - (currentTime % 1)
    currentTime = int(currentTime)
    
    return lastPrice, currentTime


def depthDataFeed():
    

    url = "https://btc-e.com/api/2/btc_usd/depth"
    
    
    
    f = urllib2.urlopen(url).read()
    
    jsonF = json.loads(f)
    
    bids = jsonF["bids"]
    asks = jsonF["asks"]
    
    curBidPrice, curBidVol = bids[0]
    curAskPrice, curAskVol = asks[0]
    
    
    return curBidPrice, curBidVol, curAskPrice, curAskVol

   
def toCandle():
    
    start = 1

    tempPrice = []
    tempOpen = []
    tempClose = []
    tempHigh = []
    tempLow = []
    tempDate = []
    oldCandleTime = 0


    while True:
        lastPrice, lastUpdate = tradeDataFeed()
        

        if start == 1:
            date = lastUpdate
            open = lastPrice
            close = lastPrice
            high = lastPrice
            low = lastPrice
            currentCandleTime = lastUpdate - (lastUpdate % timeDelta)
            oldCandleTime = currentCandleTime
            lastCandle = [dates.epoch2num(currentCandleTime),open,close, high, low]
            candleAr[-1] = lastCandle
            start = 0
            tempDate.append(currentCandleTime)
            tempPrice.append(lastPrice)

            
            
            
            
        
        currentCandleTime = lastUpdate - (lastUpdate % timeDelta)
        
        if oldCandleTime == currentCandleTime:
            
            tempDate.append(currentCandleTime)
            tempPrice.append(lastPrice)
            open = tempPrice[0]
            close = tempPrice[-1]
            high = max(tempPrice)
            low = min(tempPrice)
            lastCandle = [dates.epoch2num(currentCandleTime),open,close, high, low]
            candleAr[-1] = lastCandle
            oldCandleTime = currentCandleTime

            
            
        elif oldCandleTime != currentCandleTime:
            
            currentCandleTime = lastUpdate - (lastUpdate % timeDelta)
            
            tempPrice = []
            tempDate = []
            tempDate.append(currentCandleTime)
            tempPrice.append(lastPrice)
    
            
            open = lastPrice
            close = lastPrice
            high = lastPrice
            low = lastPrice
            lastCandle = [dates.epoch2num(currentCandleTime),open,close, high, low]
            candleAr.append(lastCandle)
            
            
            oldCandleTime = currentCandleTime


        time.sleep(8)


def simpleMovingAverage(timePeriods):
    
    values = []
    
    for digit in range(len(candleAr)):
        values.append(candleAr[digit][2])
    
    
    
    weights = np.repeat(1.0, timePeriods)/timePeriods
    smas = np.convolve(values, weights, "valid")
    return smas



def dateFunc():
    dateAr = []
    for digit in range(len(candleAr)):
        dateAr.append(candleAr[digit][0])
    return dateAr
  

 
def animate(i):
    
    #Colors
    green = "#53C156"
    red = "#ff1717"
    blue = "#3b5998"
    macolor1 = "#e1edf9"
    macolor2 = "#4ee6fd"

    rsicolor = "#1a8762"
    volumecolor = "#12e1b6"
    macdcolor1 = "#4ee6fd"
    macdcolor2 = "#e1edf9"
    yellow = "#EDD415"
    pink = "#E32DC2"
    backgroundcolor = "#07001A"
    bordercolor = "w"
    


    ax1 = plt.subplot2grid((1,9), (0,0) ,colspan=8,  axisbg=backgroundcolor) 
    ax1.clear()
    candlestick(ax1, candleAr[-40:], width=.002, colorup = green, colordown = red)
    ax1.tick_params(axis="x", colors="w")
    ax1.grid(True, color = "w")
    ax1.xaxis_date()
    ax1.yaxis.label.set_color("w")
    ax1.xaxis.label.set_color("w")
    ax1.spines["bottom"].set_color(bordercolor)
    ax1.spines["top"].set_color(bordercolor)
    ax1.spines["left"].set_color(bordercolor)
    ax1.spines["right"].set_color(bordercolor)
    ax1.tick_params(axis="y", colors="w")

    
    ############
    # Moving Average
    ############
    smaTimePeriods = 15
    dateAr = dateFunc()
    sma = simpleMovingAverage(smaTimePeriods)
    

    ax1.plot(dateAr[-40:],sma[-40:], color=macdcolor1,linewidth=1.5)
    
    
    currentBid,  currentAsk = bid_askTicker()
    lastPrice = candleAr[-1]
    lastPrice= lastPrice[2]
    differenceAsk = currentAsk - lastPrice
    differenceBid = lastPrice - currentBid
    
    bidTxt ="Ask: \n%s" % round(currentAsk,2)
    askTxt ="Bid: \n%s" % round(currentBid,2)
    currentTimeText = "Current time:  \n %s" % time.strftime('%H:%M:%S')
    

    ax2 = plt.subplot2grid((1,9), (0,8), colspan=1, axisbg=backgroundcolor)
    ax2.axis('off')
    ax2.text(0.15,0.9,currentTimeText, color = "w",fontsize=20, )
    ax2.text(0.15,0.7,bidTxt, color = green,fontsize=36, )
    ax2.text(0.15,0.6,round(abs(differenceAsk),3), color = green,fontsize=20,)  
    ax2.text(0.15,0.5,lastPrice, color = "w", fontsize=36) 
    ax2.text(0.15,0.4,round(abs(differenceBid),3), color = red,fontsize=20,) 
    ax2.text(0.15,0.2,askTxt, color = red, fontsize=36,  )

    
         
def liveGraph():
    
    print "graph."
    
    fig = plt.figure(facecolor="#07001A", figsize=(20,10))

    plt.subplots_adjust(hspace = 0.00, left = .04, bottom = .04, right = .97, top=.92)
    title = "BITFINEX 5 Minute Candles"
    plt.suptitle(title, color ="w", fontsize= 15)
    plt.ylabel("Stock Price")    
    
    anim = animation.FuncAnimation(fig, animate,
                                interval=10000)
    
    
    plt.show() 
    


currentMinutePrice = []
currentMinuteVolume = []

timeDelta = 300
candleAr = []
curBidPrice = 0
curBidVol = 0
curAskPrice = 0
curAskVol = 0
historyDateAr = []
historyPriceAr =[]
historyVolAr = []
dateL = []


dataToCandle(timeDelta)
#bid_askTicker()


#del candleAr[-1]
#print candleAr

#liveGraph()
thread2 =threading.Thread(target=toCandle).start()
time.sleep(0.01)
thread1  = threading.Thread(target=liveGraph).start()