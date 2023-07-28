import MetaTrader5 as mt5
import pandas as pd
import logging
from func_connections import connect_mt5
from constants import *

logging.basicConfig(level=logging.INFO)

VALID_DATA_TYPES = ('close', 'open', 'high', 'low', 'volume')
VALID_OUTPUT_FORMATS = ('dataframe', 'csv', 'json')

COLUMN_MAP = {
    'close': ('open', 'high', 'low', 'tick_volume', 'spread', 'real_volume'),
    'open': ('close', 'high', 'low', 'tick_volume', 'spread', 'real_volume'),
    'high': ('open', 'close', 'low', 'tick_volume', 'spread', 'real_volume'),
    'low': ('open', 'high', 'close', 'tick_volume', 'spread', 'real_volume'),
    'volume': ('open', 'high', 'low', 'close', 'spread')
}


def connect_and_execute(func):
    def wrapper(*args, **kwargs):
        if not mt5.initialize():
            logging.error("Failed to connect to MetaTrader5")
            return pd.DataFrame()
        result = func(*args, **kwargs)
        mt5.shutdown()
        return result
    return wrapper


def check_symbols(symbols):
    if not isinstance(symbols, list):
        raise TypeError("symbols argument must be a list")


def check_data_type(data_type):
    if data_type not in VALID_DATA_TYPES:
        raise ValueError(
            f"data_type argument must be one of {VALID_DATA_TYPES}")


def check_output_format(output_format):
    if output_format not in VALID_OUTPUT_FORMATS:
        raise ValueError(
            f"output_format argument must be one of {VALID_OUTPUT_FORMATS}")


def process_data_frame(df, symbol, data_type):
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df.drop(columns=[col for col in COLUMN_MAP[data_type]
            if col in df.columns], inplace=True)
    df.columns = [symbol]
    return df


def get_data_for_symbol(symbol, timeframe, count, data_type):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    return pd.DataFrame() if rates is None else process_data_frame(pd.DataFrame(rates), symbol, data_type)


@connect_and_execute
def get_data(symbols, timeframe=TIMEFRAME, count=WINDOW_LENGTH, data_type='close', output_format='dataframe') -> pd.DataFrame:
    check_symbols(symbols)
    check_data_type(data_type)
    check_output_format(output_format)

    data = pd.concat(
        [get_data_for_symbol(symbol, timeframe, count, data_type) for symbol in symbols], axis=1)

    data.dropna(inplace=True)

    return get_output(data, output_format)


def get_output(data, output_format, filename='Data'):
    try:
        if output_format == 'dataframe':
            return data
        elif output_format == 'csv':
            data.to_csv(f'{filename}.csv', index=True, header=True)
            return f'{filename}.csv created successfully'
        elif output_format == 'json':
            data.to_json(f'{filename}.json')
            return f'{filename}.json created successfully'
    except Exception as e:
        logging.error(
            f"Failed to save data to {output_format}. Error: {str(e)}")
        return f'Failed to save data to {output_format}'


@connect_and_execute
def get_spread(symbol: str) -> float:
    symbol_info = mt5.symbol_info(symbol)
    return 0 if symbol_info is None else symbol_info.spread


@connect_and_execute
def get_time(symbol: str, timeframe: int = mt5.TIMEFRAME_M5) -> int:
    try:
        time = pd.DataFrame(mt5.copy_rates_from_pos(
            symbol, timeframe, 0, 1)).loc[:, ['time']]
        return time['time'].iloc[0]
    except Exception as e:
        logging.error(
            f"Failed to get time for {symbol} {timeframe}. Error: {str(e)}")
        return 0
