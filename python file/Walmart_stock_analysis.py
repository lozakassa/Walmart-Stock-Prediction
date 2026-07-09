import pandas as pd
import matplotlib.pyplot as plt
# Updated to the modern statsmodels ARIMA import
from statsmodels.tsa.arima.model import ARIMA

# Load data (adjust to the location of your pc)
wmt_data = pd.read_csv("C:\\Users\\lozak\\OneDrive\\Desktop\\Protfolio projects\\walmart stocks\\wmt_data.csv")     

print(wmt_data.shape)
print(wmt_data.info())
print(wmt_data.isnull().sum())
print(wmt_data.describe())
print(wmt_data.head())

wmt_data['date'] = pd.to_datetime(wmt_data['date'], utc=True)
wmt_data.set_index('date', inplace=True)

wmt_data['daily_return'] = wmt_data['close'].pct_change()

wmt_data['50_day_ma'] = wmt_data['close'].rolling(window=50).mean()
wmt_data['200_day_ma'] = wmt_data['close'].rolling(window=200).mean()

print("Duplicated rows:", wmt_data.duplicated().sum())

# Walmart Stock Price and Moving Averages
plt.figure(figsize=(12,6))
plt.plot(wmt_data['close'], label='Closing Price')
plt.plot(wmt_data['50_day_ma'], label='50-day Moving Average', linestyle='--')
plt.plot(wmt_data['200_day_ma'], label='200-day Moving Average', linestyle='--')
plt.title('Walmart Stock Price and Moving Averages')
plt.legend()
plt.show()

wmt_data['20_day_ma'] = wmt_data['close'].rolling(window=20).mean()
wmt_data['20_day_std'] = wmt_data['close'].rolling(window=20).std()
wmt_data['upper_band'] = wmt_data['20_day_ma'] + (wmt_data['20_day_std'] * 2)
wmt_data['lower_band'] = wmt_data['20_day_ma'] - (wmt_data['20_day_std'] * 2)

# Plot Bollinger Bands for Walmart
plt.figure(figsize=(12,6))
plt.plot(wmt_data['close'], label='Closing Price')
plt.plot(wmt_data['upper_band'], label='Upper Band', linestyle='--')
plt.plot(wmt_data['lower_band'], label='Lower Band', linestyle='--')
plt.title('Bollinger Bands for Walmart')
plt.legend()
plt.show()

# Create trading signals based on Bollinger Bands
wmt_data['Position'] = 0  # Default no position
wmt_data.loc[wmt_data['close'] < wmt_data['lower_band'], 'Position'] = 1   # Buy
wmt_data.loc[wmt_data['close'] > wmt_data['upper_band'], 'Position'] = -1  # Sell

# Forward fill the position (keep the last signal until new one appears)
wmt_data['Position'] = wmt_data['Position'].replace(0, pd.NA).ffill()

# Plot the closing price along with Buy and Sell signals
plt.figure(figsize=(14,7))
plt.plot(wmt_data['close'], label='Closing Price', alpha=0.5)
plt.plot(wmt_data.index, wmt_data['upper_band'], label='Upper Band', linestyle='--')
plt.plot(wmt_data.index, wmt_data['lower_band'], label='Lower Band', linestyle='--')

# Plot buy signals
plt.scatter(wmt_data.index[wmt_data['Position'] == 1],
            wmt_data['close'][wmt_data['Position'] == 1],
            marker='^', color='g', s=100, label='Buy Signal')

# Plot sell signals
plt.scatter(wmt_data.index[wmt_data['Position'] == -1],
            wmt_data['close'][wmt_data['Position'] == -1],
            marker='v', color='r', s=100, label='Sell Signal')

plt.title('Walmart Trading Signals')
plt.xlabel('Date')
plt.ylabel('Closing Price ($)')
plt.legend()
plt.grid(True)
plt.show()

# Filter data for only the year 2024 (Added .copy() to prevent SettingWithCopyWarning)
wmt_data_2024 = wmt_data[(wmt_data.index.year == 2024)].copy()

# Find the points where position changes
wmt_data_2024['Signal'] = wmt_data_2024['Position'].diff()

# Plot 2024 Cleaner Version
plt.figure(figsize=(14,7))
plt.plot(wmt_data_2024.index, wmt_data_2024['close'], label='Closing Price', alpha=0.5)

# Plot buy signals (when Signal == 2)
plt.scatter(wmt_data_2024.index[wmt_data_2024['Signal'] == 2],
            wmt_data_2024['close'][wmt_data_2024['Signal'] == 2],
            marker='^', color='g', s=150, label='Buy Signal')

# Plot sell signals (when Signal == -2)
plt.scatter(wmt_data_2024.index[wmt_data_2024['Signal'] == -2],
            wmt_data_2024['close'][wmt_data_2024['Signal'] == -2],
            marker='v', color='r', s=150, label='Sell Signal')

plt.title('Walmart Trading Signals - 2024 (Cleaner Version)')
plt.xlabel('Date')
plt.ylabel('Closing Price ($)')
plt.legend()
plt.grid(True)
plt.show()

# Ensure the index is a DatetimeIndex and has a frequency set
wmt_data_2024 = wmt_data_2024.asfreq('D')  # Set the frequency to 'D' (daily data)

# Filling missing values using the modern pandas ffill() method
wmt_data_2024 = wmt_data_2024.ffill()

# Define the ARIMA model 
# Fit the model to 2024 data
model = ARIMA(wmt_data_2024['close'], order=(5, 1, 0))  # (p, d, q)
fit_model = model.fit()

# Forecast for 2025 with confidence intervals
forecast_steps = 365
forecast_result = fit_model.get_forecast(steps=forecast_steps)
forecast = forecast_result.predicted_mean
conf_int = forecast_result.conf_int(alpha=0.05) # alpha=0.05 for 95% CI

# Create a date range for 2025
forecast_index = pd.date_range(start="2025-01-01", end="2025-12-31", freq='D')

# Convert the forecast and confidence intervals to DataFrames
forecast_df = pd.DataFrame({'Predicted_Close': forecast.values}, index=forecast_index)
conf_int_df = pd.DataFrame(conf_int.values, index=forecast_index, columns=['Lower CI', 'Upper CI'])

# Plot the results
plt.figure(figsize=(14, 7))

# Plot historical data (if available)
if not wmt_data[wmt_data.index.year < 2025].empty:
    plt.plot(wmt_data[wmt_data.index.year < 2025]['close'], label='Historical Closing Prices', alpha=0.5)

# Plot the actual 2024 data
plt.plot(wmt_data_2024.index, wmt_data_2024['close'], label='Actual 2024 Closing Prices')

# Plot the forecast for 2025
plt.plot(forecast_df.index, forecast_df['Predicted_Close'], label='Forecasted 2025 Closing Prices', color='red')

# Plot the confidence intervals
plt.fill_between(conf_int_df.index,
                 conf_int_df['Lower CI'],
                 conf_int_df['Upper CI'],
                 color='red', alpha=0.2, label='95% Confidence Interval')

# Add labels, a legend, and grid
plt.title('Walmart Stock Price Prediction for 2025 with Confidence Intervals')
plt.xlabel('Date')
plt.ylabel('Closing Price ($)')
plt.legend()
plt.grid(True)

# Save and show the plot
plt.savefig('walmart_stock_predict_2025_ci.png', dpi=300, bbox_inches='tight')
plt.show()

# Print a preview of the 2025 forecast with CI
print("2025 Forecast with Confidence Intervals:")
print(pd.concat([forecast_df.head(), conf_int_df.head()], axis=1))
