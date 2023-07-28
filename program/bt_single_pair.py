import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from func_cointegration import Statistics_Cointegration
from func_public import get_data
from constants import *

# Define output subfold
output_folder = 'output_folder'
os.makedirs(output_folder, exist_ok=True)

pair = ['CADJPY', 'USDJPY']
data = get_data(pair, 5, WINDOW_LENGTH * 2)

results_list = []

for i in range(WINDOW_LENGTH, len(data)):
    window_data = data.iloc[i - WINDOW_LENGTH:i]
    arr1, arr2 = window_data.to_numpy().T

    stats = Statistics_Cointegration(arr1, arr2)

    results_list.append([
        window_data.index[-1],
        arr1[-1],
        arr2[-1],
        stats.calculate_zscore()[-1],
        stats.calculate_zscore_rolling()[-1],
        stats.calculate_half_life(),
        stats.check_cointegration(),
        stats.calculate_correlation()
    ])

# Convert the results list to a dataframe
results_df = pd.DataFrame(results_list, columns=[
                          'Date', f'{pair[0]} Close', f'{pair[1]} Close', 'Z-Score', 'Rolling Z-Score', 'Half-Life', 'Cointegrated', 'Correlation']).set_index('Date')

# Save the results dataframe to a CSV
results_df.to_csv(os.path.join(
    output_folder, f'{pair[0]}_{pair[1]}_backtest_results.csv'))

# Create subplot layout
fig = make_subplots(
    rows=7,
    cols=1,
    shared_xaxes=True,
    subplot_titles=(f'{pair[0]} Close', f'{pair[1]} Close', 'Z-Score',
                    'Rolling Z-Score', 'Half-Life', 'Cointegrated', 'Correlation'),
    vertical_spacing=0.05)

# Add traces
for i, column in enumerate(results_df.columns):
    fig.add_trace(go.Scatter(x=results_df.index,
                             y=results_df[column], name=column), row=i+1, col=1)

# Update layout
fig.update_layout(
    height=2500, title_text=f"{pair[0]} and {pair[1]} Backtest Results", showlegend=False)

# Save to HTML
fig.write_html(os.path.join(
    output_folder, f'{pair[0]}_{pair[1]}_backtest_results.html'))
