# algo.py
import time
import logging
from tvDatafeed import TvDatafeed, Interval
from talipp.indicators import EMA, RSI, BB, StdDev
from datetime import datetime, timezone
from bot.models import Token
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

freq_in_mins = 15

LEVERAGE = "cross (10x)"
RISK = "2%"

def utctime():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def checkdecimal(number1):
    count = 0
    while number1 - int(number1) > 0.000001:
        number1 *= 10
        count += 1
    return count

def get_data_with_backoff(tv_instance, symbol, max_retries=5, initial_delay=1, factor=2):
    """
    Attempts to fetch historical data with exponential backoff.
    If the maximum number of retries is exceeded, returns None.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            data = tv_instance.get_hist(symbol=symbol, interval=Interval.in_15_minute, n_bars=700)
            if data is not None:
                logging.info(f"{symbol} - Data fetched successfully on attempt {attempt}")
                return data
        except Exception as e:
            logging.warning(f"{symbol} - Attempt {attempt}/{max_retries} error: {e}", exc_info=True)
        time.sleep(delay)
        delay *= factor  # exponential backoff
    logging.error(f"{symbol}: Cannot fetch data after {max_retries} attempts.")
    return None

def format_symbol(symbol_name):
    """Convert BINANCE:RSRUSDT.P to RSR/USDT"""
    try:
        exchange, token = symbol_name.split(':')
        base = token.replace('USDT.P', '').replace('USDT', '')
        return f"{base}/USDT"
    except Exception as e:
        logging.error(f"Error formatting symbol {symbol_name}: {e}")
        return symbol_name  # fallback to original
    
def calculate_targets(close_price, decimal_places, ema200_value, signal_type):
    """Calculate TP/SL levels based on signal type (long/short)"""
    entry = round(close_price, decimal_places)
    sl_target = None
    tp_ratio_percent = None

    # Determine SL and TP ratio based on signal type
    if "Long" in signal_type:
        # Long trade: SL = EMA200 * 0.99
        sl_target = round(ema200_value * 0.99, decimal_places)
        tp_ratio_percent = (abs((sl_target / entry)-1))
        tp_targets = [
            round(entry * (1 + tp_ratio_percent), decimal_places),
            round(entry * (1 + (tp_ratio_percent * 2)), decimal_places),
            round(entry * (1 + (tp_ratio_percent * 3)), decimal_places),
            round(entry * (1 + (tp_ratio_percent * 4)), decimal_places)
        ]
    else:
        # Short trade: SL = EMA200 * 1.01
        sl_target = round(ema200_value * 1.01, decimal_places)
        tp_ratio_percent = (abs((sl_target / entry)-1)) 
        tp_targets = [
            round(entry * (1 - tp_ratio_percent), decimal_places),
            round(entry * (1 - (tp_ratio_percent * 2)), decimal_places),
            round(entry * (1 - (tp_ratio_percent * 3)), decimal_places),
            round(entry * (1 - (tp_ratio_percent * 4)), decimal_places)
        ]

    return {
        'entry': [entry],
        'ema_200': ema200_value,
        'tp': tp_targets,  # Now includes 4 targets
        'sl': sl_target
    }
    
def create_signal_message(symbol_name, signal_type, close_price, decimal_places, ema200_value):
    """Create formatted message with targets"""
    formatted_symbol = format_symbol(symbol_name)
    targets = calculate_targets(close_price, decimal_places, ema200_value, signal_type)
    
    return (
        f"⚡⚡ #{formatted_symbol} ⚡⚡\n\n"
        f"Signal Type: {signal_type}\n"
        f"Leverage: {LEVERAGE}\n"
        f"RISK: {RISK}\n\n"
        f"EMA Value: {targets['ema_200']}\n"
        "Entry Targets:\n"
        f"1) {targets['entry'][0]}\n\n"
        "Take-Profit Targets:\n"
        f"1) {targets['tp'][0]}\n"
        f"2) {targets['tp'][1]}\n"
        f"3) {targets['tp'][2]}\n"
        f"4) {targets['tp'][3]}\n\n"
        "Stop Targets:\n"
        f"1) {targets['sl']}\n\n"
        "Trailing Configuration:\n"
        "Stop: Moving Target - Trigger: Target (1)\n"
        f"UTC: {utctime()}"
    )
    
def get_symbols_from_db():
    """
    Fetch token symbols from the database dynamically.
    """
    return [f"{token[0]}:{token[1]}" for token in Token.objects.values_list('exchange', 'token_symbol')]

def run_analysis():
    """
    Runs one cycle of analysis and returns a list of signal messages.
    """
    messages = []
    # Initialize TvDatafeed using your credentials.
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    tv = TvDatafeed(username, password)
    
    # List of symbols to analyze.
    symbols = get_symbols_from_db()
    
    for symbol in symbols:
        logging.info(f"Processing symbol: {symbol}")
        data = get_data_with_backoff(tv, symbol)
        if data is None:
            logging.warning(f"{symbol}: Cannot fetch data after retries")
            continue
        if len(data) < 502:
            logging.warning(f"{symbol}: Insufficient data returned ({len(data)} bars)")
            continue

        symbol_name = data['symbol'].tolist()[0]
        open1 = data['open'].tolist()
        high1 = data['high'].tolist()
        low1 = data['low'].tolist()
        close1 = data['close'].tolist()
        decimal = max(checkdecimal(open1[-1]), checkdecimal(close1[-1]))

        # Calculate indicators
        rsi = [0 if v is None else round(v, 2) for v in RSI(period=14, input_values=close1)]
        rsiema = [0 if v is None else round(v, 2) for v in EMA(period=14, input_values=rsi)]
        ema14 = [0 if v is None else round(v, decimal) for v in EMA(period=14, input_values=close1)]
        ema200 = [0 if v is None else round(v, decimal) for v in EMA(period=200, input_values=close1)]
        bb = BB(period=20, std_dev_mult=2.0, input_values=rsi)
        bbmid = [0 if elem is None else round(elem, decimal) for elem in bb.central_band]
        std_dev = [0 if v is None else v for v in StdDev(period=20, input_values=rsi)]
        upper = []
        lower = []
        for count, mid in enumerate(bbmid):
            upper.append(mid + (std_dev[count] * 2.0))
            lower.append(mid - (std_dev[count] * 2.0))
        upper = [0 if v is None else round(v, decimal) for v in upper]
        lower = [0 if v is None else round(v, decimal) for v in lower]

        trend = 0
        for i in range(-2, -502, -1):
            if rsi[i] >= upper[i]:
                trend = -1
                break
            if rsi[i] <= lower[i]:
                trend = 1
                break

        trend2 = 0
        for index1 in range(-3, -502, -1):
            long_conditions = all([
                rsi[index1] > rsiema[index1],
                rsi[index1] > bbmid[index1],
                ema14[index1] > ema200[index1],
                close1[index1] > ema14[index1],
                rsi[index1] < 50
            ])
            short_conditions = all([
                rsi[index1] < rsiema[index1],
                rsi[index1] < bbmid[index1],
                ema14[index1] < ema200[index1],
                close1[index1] < ema14[index1],
                rsi[index1] > 50
            ])
            if long_conditions:
                trend2 = 1
                break
            if short_conditions:
                trend2 = -1
                break

        buylist = []
        selllist = []
        for index1 in range(-2, -4, -1):
            buylist.append(all([
                rsi[index1] > rsiema[index1],
                rsi[index1] > bbmid[index1],
                ema14[index1] > ema200[index1],
                close1[index1] > ema14[index1],
                rsi[index1] < 50
            ]))
            selllist.append(all([
                rsi[index1] < rsiema[index1],
                rsi[index1] < bbmid[index1],
                ema14[index1] < ema200[index1],
                close1[index1] < ema14[index1],
                rsi[index1] > 50
            ]))
        buysignal = buylist[0] and not buylist[1] and trend == 1 and trend2 < 1
        sellsignal = selllist[0] and not selllist[1] and trend == -1 and trend2 > -1
        buysignal1 = buylist[0] and not buylist[1] and trend == 1 and trend2 == 1
        sellsignal1 = selllist[0] and not selllist[1] and trend == -1 and trend2 == -1

        if buysignal:
            message = create_signal_message(
                symbol_name, 
                "Regular (Long)", 
                close1[-1],
                decimal,
                ema200[-1]
            )
            messages.append(message)
        if sellsignal:
            message = create_signal_message(
                symbol_name, 
                "Regular (Short)", 
                close1[-1],
                decimal,
                ema200[-1]
            )
            messages.append(message)
        if buysignal1:
            message = create_signal_message(
                symbol_name, 
                "Compound (Long)", 
                close1[-1],
                decimal,
                ema200[-1]
            )
            messages.append(message)
        if sellsignal1:
            message = create_signal_message(
                symbol_name, 
                "Compound (Short)", 
                close1[-1],
                decimal,
                ema200[-1]
            )
            messages.append(message)

    return messages

if __name__ == "__main__":
    # For testing purposes, run one analysis cycle and print any signals.
    signals = run_analysis()
    for sig in signals:
        print(sig)
