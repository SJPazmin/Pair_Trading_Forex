from typing import Optional
from constants import *


class PairTradingAgent:
    def __init__(
        self,
        symbol_1: str,
        symbol_2: str,
        ticket_1: Optional[int] = None,
        ticket_2: Optional[int] = None,
        z_score: float = 0.0,
        z_score_rolling: float = 0.0,
        half_life: float = 0.0,
        hedge_ratio: float = 0.0,
    ):
        self.symbol_1 = symbol_1
        self.symbol_2 = symbol_2
        self.ticket_1 = ticket_1
        self.ticket_2 = ticket_2
        self.z_score = z_score
        self.z_score_rolling = z_score_rolling
        self.half_life = half_life
        self.hedge_ratio = hedge_ratio

    @property
    def trade_data(self):
        return {
            "symbol_1": self.symbol_1,
            "symbol_2": self.symbol_2,
            "ticket_1": self.ticket_1,
            "ticket_2": self.ticket_2,
            "z_score": self.z_score,
            "z_score_rolling": self.z_score_rolling,
            "half_life": self.half_life,
            "hedge_ratio": self.hedge_ratio,
        }
