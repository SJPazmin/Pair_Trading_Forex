import logging
import time
from constants import *
from func_connections import connect_mt5
from func_storage_cointegration import store_cointegration_results
from func_public import get_time

# Setup logging
logging.basicConfig(level=logging.INFO)

# MAIN FUNCTION
if __name__ == "__main__":

    # Initialize variables
    last_candle_time = 0

    # Connect to client
    try:
        logging.info("Connecting to Client...")
        client = connect_mt5()
    except Exception as e:
        logging.error("Error connecting to client: ", str(e))
        exit(1)

    # Run as always on
    while True:
        try:
            # Find Cointegrated Pairs
            if FIND_COINTEGRATED and last_candle_time != get_time('EURUSD', 5):
                # Store Cointegrated Pairs
                logging.info("Storing cointegrated pairs...")
                stores_result = store_cointegration_results()
                last_candle_time = get_time('EURUSD', 5)
                if not stores_result:
                    logging.info("Empty cointegrated pairs list for trading")

            # Place trades for opening positions
            if MANAGE_EXITS:
                logging.info("Managing exits...")
                # manage_trade_exits(client)

            # Place trades for opening positions
            if PLACE_TRADES:
                logging.info("Finding trading opportunities...")
                # open_positions(client)

            # Configurable delay, tune this as per your requirements.
            time.sleep(10)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            exit(1)
