# Import necessary functions and constants
from func_cointegration import Statistics_Cointegration
from func_public import get_data
from constants import *

# Define the currency pair to analyze
pair = ['CADJPY', 'USDJPY']

# Get the data for the currency pair
data = get_data(pair)

# Separate the data into two arrays
arr1, arr2 = data.to_numpy().T

# Calculate statistics for the cointegration of the two arrays
stats = Statistics_Cointegration(arr1, arr2)

# Calculate the correlation between the two arrays
correlation = stats.calculate_correlation()

# Check if the two arrays are cointegrated
cointegrated = stats.check_cointegration()

# Calculate the half-life of the cointegration
half_life = stats.calculate_half_life()

# Calculate the z-score of the cointegration
zscore = stats.calculate_zscore()[-1]

# Calculate the rolling z-score of the cointegration
zscore_rolling = stats.calculate_zscore_rolling()[-1]

# Print the results in a readable format
print(f"Currency Pair: {pair}")
print(f"Correlation: {correlation}")
print(f"Cointegrated: {cointegrated}")
print(f"Half-Life: {half_life}")
print(f"Z-Score: {zscore}")
print(f"Rolling Z-Score: {zscore_rolling}")
