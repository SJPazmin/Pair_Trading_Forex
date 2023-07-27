import json
import logging
import numpy as np
from typing import List, Dict
from contextlib import suppress
from constants import *
from func_public import get_data, get_spread
from func_cointegration import Statistics_Cointegration
from func_private import (
    place_market_order,
    close_order_by_ticket,
    check_existing_trades,
    OrderType,
)
from func_bot_agent import PairTradingAgent

logging.basicConfig(level=logging.DEBUG)


class TradeConditions:
    def __init__(self, pair: List[str], hedge_ratio: float, zscore: float, zscore_rolling: float, half_life: float):
        self.pair = pair
        self.hedge_ratio = hedge_ratio
        self.zscore = zscore
        self.zscore_rolling = zscore_rolling
        self.half_life = half_life

    def to_dict(self) -> Dict:
        return {
            "pair": self.pair,
            "hedge_ratio": self.hedge_ratio,
            "zscore": self.zscore,
            "zscore_rolling": self.zscore_rolling,
            "half_life": self.half_life,
        }


def load_cointegrated_pairs() -> List:
    with suppress(FileNotFoundError, json.JSONDecodeError):
        with open(COINTEGRATED_PAIRS_FILE, 'r') as file:
            return json.load(file)
    return []


def check_pair_trade_conditions(pair: List[str]) -> TradeConditions:
    data = get_data(pair)
    arr1 = np.array(data.iloc[:, 0])
    arr2 = np.array(data.iloc[:, 1])
    stats = Statistics_Cointegration(arr1, arr2)
    correlation = stats.calculate_correlation()
    cointegrated = stats.check_cointegration()
    half_life = stats.calculate_half_life()
    zscore = stats.calculate_zscore()[-1]
    zscore_rolling = stats.calculate_zscore_rolling()[-1]
    total_spread_points = get_spread(pair[0]) + get_spread(pair[1])

    if (
        correlation > CORRELATION_THRESHOLD
        and not cointegrated
        and half_life <= MAX_HALF_LIFE
        and abs(zscore) >= Z_SCORE_THRESHOLD
        and abs(zscore_rolling) >= Z_SCORE_THRESHOLD
        and total_spread_points <= MAX_SPREAD_POINTS
    ):
        return TradeConditions(pair, stats.hedge_ratio, zscore, zscore_rolling, half_life)
    return None


def load_open_trades() -> List:
    with suppress(FileNotFoundError, json.JSONDecodeError):
        with open(OPEN_TRADES_FILE, 'r') as file:
            return json.load(file)
    return []


def open_positions():
    pairs = load_cointegrated_pairs()
    if not pairs:
        logging.info("No cointegrated pairs found, exiting...")
        return

    open_trades = load_open_trades()

    for pair in pairs:
        open_positions_for_pair(pair, open_trades)


def open_positions_for_pair(pair, open_trades):
    if check_existing_trades(pair, open_trades):
        logging.info(f"Trade already exists for pair: {pair}, skipping...")
        return

    trade_conditions = check_pair_trade_conditions(pair)
    if trade_conditions:
        symbol1_order_type = OrderType.SELL if trade_conditions.zscore > 0 else OrderType.BUY
        symbol2_order_type = OrderType.SELL if trade_conditions.zscore < 0 else OrderType.BUY
        symbol1_lot_size = LOT_SIZE
        symbol2_lot_size = round(
            LOT_SIZE * trade_conditions.hedge_ratio, 2)
        symbol1_ticket = place_market_order(
            pair[0], symbol1_order_type, symbol1_lot_size)
        symbol2_ticket = place_market_order(
            pair[1], symbol2_order_type, symbol2_lot_size)

        if not symbol1_ticket or not symbol2_ticket:
            close_order_by_ticket(symbol1_ticket)
            close_order_by_ticket(symbol2_ticket)
            logging.warning(f"Unable to open trades for pair: {pair}")
            return

        agent = PairTradingAgent(
            pair[0],
            pair[1],
            symbol1_ticket,
            symbol2_ticket,
            trade_conditions.zscore,
            trade_conditions.zscore_rolling,
            trade_conditions.half_life,
            trade_conditions.hedge_ratio,
        )
        open_trades.append(agent.trade_data)

        with open(OPEN_TRADES_FILE, 'w') as file:
            json.dump(open_trades, file)
