"""Forecasting - simple time series forecast for next month"""
import pandas as pd
import numpy as np


def simple_forecast(time_series, periods=1):
    """
    Simple exponential smoothing / moving average forecast.
    Args:
        time_series: Series with datetime index and numeric values
        periods: number of periods to forecast (default 1 month)
    Returns:
        forecast values
    """
    if len(time_series) < 2:
        return [time_series.iloc[-1] if len(time_series) > 0 else 0] * periods
    
    # Simple: use last 3 months average or all available data
    recent = time_series.iloc[-3:] if len(time_series) >= 3 else time_series
    avg = recent.mean()
    
    # Forecast next periods with simple moving average
    forecast = [avg] * periods
    return forecast


def forecast_funnel_metrics(monthly_data):
    """
    Forecast next month's funnel metrics (searches, registrations, jobs).
    Args:
        monthly_data: DataFrame with monthly aggregated metrics
    Returns:
        DataFrame with forecast for next month
    """
    if monthly_data.empty:
        return pd.DataFrame()
    
    forecasts = {}
    for col in ['searches', 'registrations', 'jobs']:
        if col in monthly_data.columns:
            ts = pd.Series(monthly_data[col].values)
            forecasts[col] = simple_forecast(ts, periods=1)[0]
    
    return forecasts
