import json
import numpy as np
from constants import *
from func_cointegration import Statistics_Cointegration
from func_public import get_data

# Store Cointegration Results


def store_cointegration_results():
    global MAX_HALF_LIFE

    # Attempt to load JSON file containing currency pairs to check
    try:
        with open('pairs_corr.json', 'r') as file:
            pairs = json.load(file)
    except Exception as e:
        print(f"Error in loading JSON file: {e}")
        return []

    # Initialize list to store cointegrated pairs
    cointegrated_pairs = []

    # Iterate over each pair
    for pair in pairs:
        # Get data for the given pair
        data = get_data(pair, TIMEFRAME, WINDOW_LENGTH, 'close', 'dataframe')

        # Split data into two arrays for analysis
        arr1 = np.array(data.iloc[:, 0])
        arr2 = np.array(data.iloc[:, 1])

        # Initialize ForexStats class with the two time series
        statistics = Statistics_Cointegration(arr1, arr2)

        # If pair is highly correlated, cointegrated, and has a half-life less than or equal to 35
        if statistics.calculate_correlation() > CORRELATION_THRESHOLD and not statistics.check_cointegration() and statistics.calculate_half_life() <= MAX_HALF_LIFE:
            # Add to the list of cointegrated pairs
            cointegrated_pairs.append(pair)

    # Save cointegrated pairs to JSON file for later use
    try:
        with open(COINTEGRATED_PAIRS_FILE, 'w') as file:
            # Convert the list of pairs to a json string and write it to the file
            json.dump(cointegrated_pairs, file)
    except Exception as e:
        print(f"Error in saving cointegrated pairs: {e}")

    return cointegrated_pairs
