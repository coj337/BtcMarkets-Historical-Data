import urllib.request
import json
import time
from datetime import datetime
import csv

pair = "BTC/AUD"
earliestTime = "1377838800000"
ticks = []
intervals = ["Day", "Hour", "Minute"]

def GetTickData(pair, timestamp, interval):
    responseString = urllib.request.urlopen("https://api.btcmarkets.net/v2/market/" + pair + "/tickByTime/" + interval.lower() + "?sortForward=true&indexForward=true&since=" + timestamp).read()
    return json.loads(responseString)

def NormalizeData(unformattedTicks):
    del unformattedTicks[-1] # Accidentally grabs the last one twice
    for tick in unformattedTicks: # Convert to readable numbers
        tick["timestamp"] = tick["timestamp"] / 1000
        tick["open"] = tick["open"] / 100000000
        tick["high"] = tick["high"] / 100000000
        tick["low"] = tick["low"] / 100000000
        tick["close"] = tick["close"] / 100000000
        tick["volume"] = tick["volume"] / 100000000
    return unformattedTicks

for interval in intervals:
    print("Downloading " + interval.lower() + " historical data from BtcMarkets.")

    upToDate = False
    lastTime = earliestTime
    while not upToDate:
        data = GetTickData(pair, lastTime, interval)
        if data["paging"]["newer"].split("&since=")[1] == lastTime:
            upToDate = True
        lastTime = data["paging"]["newer"].split("&since=")[1]
        
        normalizedTicks = NormalizeData(data["ticks"])
        ticks.extend(normalizedTicks)
        
        print("Downloaded 3000 ticks from " + datetime.utcfromtimestamp((int(lastTime) / 1000)).strftime('%Y-%m-%d'))
        time.sleep(1)

    print("Successfully downloaded (" + interval + ") historical data.")

    with open("BtcMarkets-" + interval + "-OHLC.csv", 'w', newline='') as f:
        w = csv.DictWriter(f, ["timestamp", "open", "high", "low", "close", "volume"])
        w.writeheader()
        w.writerows(ticks)

    print("Saved data to BtcMarkets-" + interval + "-OHLC.csv\n")
