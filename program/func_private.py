import MetaTrader5 as mt5
import logging
from func_connections import connect_mt5
from typing import List, Union
from enum import Enum


class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"


logging.basicConfig(level=logging.INFO)


def connect_and_execute(func):
    """
    Decorator function to establish a connection before executing a given function.
    """
    def wrapper(*args, **kwargs):
        if not connect_mt5():
            logging.error('Failed to connect to MT5')
            return None  # or raise an Exception
        return func(*args, **kwargs)
    return wrapper


def is_open_positions(symbol_x: str, symbol_y: str) -> bool:
    """
    Checks if there are open positions for the given symbols.
    """
    positions = mt5.positions_get()
    for position in positions:
        if position.symbol == symbol_x or position.symbol == symbol_y:
            return True
    return False


def build_request(symbol: str, volume: float, order_type: OrderType, ticket: Union[int, None] = None,
                  magic_number: int = 0, comment: str = "") -> dict:
    """
    Builds a request for placing an order.
    """
    _type = mt5.ORDER_TYPE_BUY if order_type == OrderType.BUY else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": _type,
        "magic": magic_number,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    if ticket:
        request["position"] = ticket

    return request


def send_order(request: dict) -> Union[int, None]:
    """
    Sends an order to MT5. Returns order number if successful, None otherwise.
    """
    check = mt5.order_check(request)
    if check is None or check.retcode != 0:
        logging.error(
            f"Order check failed with error code: {check.retcode if check is not None else 'None'}")
        return None

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(f"Order failed with error code: {result.retcode}")
        return None

    return result.order


@connect_and_execute
def place_market_order(symbol: str, type: OrderType, volume: float, magic_number: int = 0, comment: str = "") -> int:
    """
    Places a market order.
    """
    request = build_request(symbol, volume, type,
                            magic_number=magic_number, comment=comment)
    return send_order(request)


@connect_and_execute
def close_order_by_ticket(ticket: int, comment: str = "") -> Union[int, None]:
    """
    Closes an order by ticket.
    """
    position_info = mt5.positions_get(ticket=ticket)
    if position_info == ():
        logging.error(f"No positions with ticket {ticket}")
        return None

    symbol = position_info[0].symbol
    volume = position_info[0].volume
    order_type = OrderType.BUY if position_info[0].type == 1 else OrderType.SELL
    magic_number = position_info[0].magic

    request = build_request(symbol, volume, order_type,
                            ticket=ticket, magic_number=magic_number, comment=comment)
    return send_order(request)


@connect_and_execute
def modify_order(ticket: int, stop_loss: float, take_profit: float, comment: str = "") -> bool:
    """
    Modifies an existing order.
    """
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": stop_loss,
        "tp": take_profit,
        "comment": comment
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(
            f"Modify Order failed, retcode={result.retcode} - {result.comment}")
        return False

    logging.info(f"Order {result.order} Modified, comment = {result.comment}")
    return True


def check_existing_trades(pair: List[str], open_trades: List[dict]) -> bool:
    """
    Checks if there are existing trades for a given pair.
    """
    pair_set = set(pair)
    for trade in open_trades:
        if pair_set == {trade['symbol_1'], trade['symbol_2']}:
            return True
    return False
