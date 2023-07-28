import json
import logging
from typing import List, Dict, Optional
from contextlib import suppress
from constants import *
from func_public import get_data, get_spread
from func_cointegration import Statistics_Cointegration
from func_private import close_order_by_ticket

logging.basicConfig(level=logging.DEBUG)

# Define a class to represent position data


class PositionData:
    def __init__(self, pair: List[str], position_1: int, position_2: int):
        self.pair = pair
        self.position_1 = position_1
        self.position_2 = position_2

    def to_dict(self) -> Dict:
        return {
            "pair": self.pair,
            "position_1": self.position_1,
            "position_2": self.position_2,
        }


# Load data from a file, suppressing exceptions if the file is not found or not in JSON format
def load_from_file(filepath) -> List:
    with suppress(FileNotFoundError, json.JSONDecodeError):
        with open(filepath, 'r') as file:
            return json.load(file)
    return []


# Check conditions to close a pair of positions
def check_pair_close_conditions(position: List[Dict]) -> Optional[PositionData]:
    pair = [position['symbol_1'], position['symbol_2']]
    data = get_data(pair)
    arr1, arr2 = data.to_numpy().T
    stats = Statistics_Cointegration(arr1, arr2)
    zscore = stats.calculate_zscore()[-1]
    zscore_rolling = stats.calculate_zscore_rolling()[-1]
    total_spread_points = sum(get_spread(symbol) for symbol in pair)
    cross_zscore = (zscore < 0 and position['z_score'] > 0) or (
        zscore > 0 and position['z_score'] < 0)
    cross_zscore_rolling = (zscore_rolling < 0 and position['z_score_rolling'] > 0) or (
        zscore_rolling > 0 and position['z_score_rolling'] < 0)

    if (
        cross_zscore
        and cross_zscore_rolling
        and total_spread_points <= MAX_SPREAD_POINTS
    ):
        return PositionData(pair, position['ticket_1'], position['ticket_2'])
    return None


# Close positions for a pair of positions
def close_positions_for_pair(position: List[Dict], remaining_positions_for_pair: List[Dict]):

    close_conditions = check_pair_close_conditions(position)
    if close_conditions:

        # Close both positions by their ticket numbers
        close_ticket_1 = close_order_by_ticket(close_conditions.position_1)
        close_ticket_2 = close_order_by_ticket(close_conditions.position_2)

        return

    # Append the current position to the list of remaining positions for the pair
    remaining_positions_for_pair.append(position)


# Close all open positions
def close_positions():
    current_positions_for_pair = load_from_file(OPEN_TRADES_FILE)
    if not current_positions_for_pair:
        logging.info("No open trades to close")
        return

    remaining_positions_for_pair = []

    # Iterate through each position and close them if conditions are met
    for position in current_positions_for_pair:
        close_positions_for_pair(position, remaining_positions_for_pair)

    # Write the remaining open positions back to the file
    with open(OPEN_TRADES_FILE, 'w') as file:
        json.dump(remaining_positions_for_pair, file)
