from func_private import *

# Test connection to MT5


def test_connect_mt5():
    assert connect_mt5() == True

# Test is_open_positions function


def test_is_open_positions():
    assert is_open_positions("EURUSD", "GBPUSD") == False

# Test build_request function


def test_build_request():
    request = build_request("EURUSD", 0.01, OrderType.BUY)
    assert request["symbol"] == "EURUSD"
    assert request["volume"] == 0.01
    assert request["type"] == mt5.ORDER_TYPE_BUY

# Test send_order function


def test_send_order():
    request = build_request("EURUSD", 0.01, OrderType.BUY)
    assert send_order(request) != None

# Test place_market_order function


def test_place_market_order():
    assert place_market_order("EURUSD", OrderType.BUY, 0.01) != None

# Test close_order_by_ticket function


def test_close_order_by_ticket():
    # Open a new order
    ticket = place_market_order("EURUSD", OrderType.BUY, 0.01)
    assert close_order_by_ticket(ticket) != None

# Test modify_order function


def test_modify_order():
    # Open a new order
    ticket = place_market_order("EURUSD", OrderType.BUY, 0.01)
    assert modify_order(ticket, 1.0, 1.5) == True

# Test check_existing_trades function


def test_check_existing_trades():
    # Open a new order
    ticket = place_market_order("EURUSD", OrderType.BUY, 0.01)
    open_trades = [{"symbol_1": "EURUSD", "symbol_2": "GBPUSD"}]
    assert check_existing_trades(["EURUSD", "GBPUSD"], open_trades) == True
