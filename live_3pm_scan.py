from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import datetime
import time
import os

# Initialize TradingView
tv = TvDatafeed()

# Read the symbols from the text file
def get_symbols():
    if not os.path.exists("symbols.txt"):
        print("ERROR: symbols.txt not found!")
        return ['LOTCHEM'] # Fallback
    
    with open("symbols.txt", "r") as f:
        # Read lines, remove spaces/newlines, and ignore empty lines
        symbols = [line.strip() for line in f if line.strip()]
    return symbols

def check_live_setup(symbol):
    try:
        # 1. Fetch Daily Data
        daily = tv.get_hist(symbol=symbol, exchange='PSX', interval=Interval.in_daily, n_bars=10)
        if daily is None or len(daily) < 3:
            return # Skip quietly if data is missing
            
        # 2. Fetch Intraday Data
        intraday = tv.get_hist(symbol=symbol, exchange='PSX', interval=Interval.in_1_minute, n_bars=500)
        if intraday is None or intraday.empty:
             return

        # Filter for TODAY
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        today_data = intraday[intraday.index.strftime('%Y-%m-%d') == today_str]
        
        if today_data.empty:
            return 

        # Build Live Candle
        live_open = today_data['open'].iloc[0]
        live_close = today_data['close'].iloc[-1]
        live_volume = today_data['volume'].sum()

        # Get Yesterday's Data
        yesterday = daily.iloc[-2] 
        prev_open = yesterday['open']
        prev_close = yesterday['close']
        prev_vol = yesterday['volume']
        prev_low = yesterday['low']
        
        # Your Logic
        prev_is_red = prev_close < prev_open
        is_green = live_close > live_open
        low_vol = live_volume < prev_vol

        # Signal Check
        if prev_is_red and is_green and low_vol:
            print(f"\n🚨 SIGNAL: {symbol} at {datetime.datetime.now().strftime('%H:%M')}")
            print(f"   Yesterday (Red): Close={prev_close:.2f}, Vol={prev_vol}")
            print(f"   Today (Green): Open={live_open:.2f}, Close={live_close:.2f}, Vol={live_volume}")
            print(f"   STOP LOSS: {prev_low:.2f}")
            print("-" * 50)

    except Exception as e:
        # We use 'pass' here so if one stock fails, it doesn't stop the whole scanner
        pass 

if __name__ == "__main__":
    symbols_list = get_symbols()
    print(f"=== STARTING SCAN OF {len(symbols_list)} SYMBOLS ===")
    
    for i, sym in enumerate(symbols_list):
        # Optional: Print a dot for every stock checked so you know it's working
        print(f"Checking {sym}... ({i+1}/{len(symbols_list)})", end="\r")
        check_live_setup(sym)
        
        # CRITICAL: Wait 1.5 seconds between stocks to prevent TradingView from blocking us
        time.sleep(1.5) 
        
    print("\n=== SCAN COMPLETE ===")
