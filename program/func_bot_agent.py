from func_private import place_market_order
from datetime import datetime
from typing import Optional
from constants import *
from func_private import place_market_order, close_order_by_ticket


class PairTradingAgent:
    def __init__(
        self,
        symbol_x: str,
        symbol_y: str,
        ticket_x: Optional[int] = None,
        ticket_y: Optional[int] = None,
        spread: float = 0.0,
        z_score: float = 0.0,
        half_life: float = 0.0,
        hedge_ratio: float = 0.0,
    ):
        self.symbol_x = symbol_x
        self.symbol_y = symbol_y
        self.ticket_x = ticket_x
        self.ticket_y = ticket_y
        self.spread = spread
        self.z_score = z_score
        self.half_life = half_life
        self.hedge_ratio = hedge_ratio
