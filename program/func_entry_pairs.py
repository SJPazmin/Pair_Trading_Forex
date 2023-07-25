import json

from constants import *
from func_public import get_data
from func_cointegration import Statistics_Cointegration

# Open positions


def open_positions(client):
    """
      Manage finding triggers for trade entry
      Store trades for managing later on on exit function
    """

    # Attempt to load JSON file containing currency pairs cointegrated
    try:
        with open(COINTEGRATED_PAIRS_FILE, 'r') as file:
            pairs = json.load(file)
    except Exception as e:
        print(f"Error in loading JSON file: {e}")
        pairs = []

    # Initialize container for trading pairs open and their statistics
    trading_pairs = []
