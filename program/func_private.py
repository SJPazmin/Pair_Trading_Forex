import MetaTrader5 as mt5
import logging
from func_connections import connect_mt5

ACTION = mt5.TRADE_ACTION_DEAL
FILLING = mt5.ORDER_FILLING_IOC
TIME = mt5.ORDER_TIME_GTC

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def connect_and_execute(func):
    def wrapper(*args, **kwargs):
        connect_mt5()
        return func(*args, **kwargs)
    return wrapper


def is_open_positions(symbol_x, symbol_y):
    positions = mt5.positions_get()
    for position in positions:
        if position.symbol == symbol_x or position.symbol == symbol_y:
            return True
    return False


def build_request(symbol, volume, type, ticket=None, magic_number=0, comment=""):
    order_type = mt5.ORDER_TYPE_BUY if type == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": ACTION,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "magic": magic_number,
        "comment": comment,
        "type_time": TIME,
        "type_filling": FILLING
    }

    if ticket:
        request["position"] = ticket

    return request


@connect_and_execute
def place_market_order(symbol, type, volume, magic_number=0, comment="") -> int:
    request = build_request(symbol, volume, type,
                            magic_number=magic_number, comment=comment)

    # Check if the order request is valid
    check = mt5.order_check(request)
    if check is None or check.retcode != 0:
        logging.error(
            f"Order check failed with error code: {check.retcode if check is not None else 'None'}")
        return None

    # Send the order request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(f"Order failed with error code: {result.retcode}")
        return None

    # Return the order number
    return result.order


@connect_and_execute
def close_order_by_ticket(ticket, comment=""):
    # Get the position details
    position_info = mt5.positions_get(ticket=ticket)
    if position_info == ():
        logging.error(f"No positions with ticket {ticket}")
        return None

    # Extract the necessary details from the position
    symbol = position_info[0].symbol
    volume = position_info[0].volume
    order_type = "buy" if position_info[0].type == 1 else "sell"
    magic_number = position_info[0].magic

    # Build the request dict
    request = build_request(symbol, volume, order_type,
                            ticket=ticket, magic_number=magic_number, comment=comment)

    # Send the close order request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(
            f"Position Close failed, retcode={result.retcode} - {result.comment}")
        return None

    logging.info(
        f"Position {result.order} Closed on {request['symbol']}, comment = {result.comment}")
    return True


@connect_and_execute
def modify_order(ticket, stop_loss, take_profit, comment=""):
    # Build the request dict
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": stop_loss,
        "tp": take_profit,
        "comment": comment
    }

    # Send the modify order request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(
            f"Modify Order failed, retcode={result.retcode} - {result.comment}")
        return None

    logging.info(f"Order {result.order} Modified, comment = {result.comment}")
    return True
