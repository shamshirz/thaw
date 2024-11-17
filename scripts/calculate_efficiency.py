import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_efficiency_metrics(utility_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cost and usage efficiency metrics using degree days
    Returns DataFrame with cost per degree day and usage per degree day
    """
    logger.info("Calculating efficiency metrics...")
    
    # Ensure dates are in the same format and reset weather data index
    utility_data['date'] = pd.to_datetime(utility_data['date'])
    weather_data = weather_data.reset_index()
    
    # Rename 'time' column to 'date' in weather data
    weather_data = weather_data.rename(columns={'time': 'date'})
    weather_data['date'] = pd.to_datetime(weather_data['date'])
    
    # Format dates to first of month for proper joining
    utility_data['date'] = utility_data['date'].dt.to_period('M').dt.to_timestamp()
    weather_data['date'] = weather_data['date'].dt.to_period('M').dt.to_timestamp()
    
    # Debug logging
    logger.info(f"Utility data date range: {utility_data['date'].min()} to {utility_data['date'].max()}")
    logger.info(f"Weather data date range: {weather_data['date'].min()} to {weather_data['date'].max()}")
    
    # Merge the datasets
    df = pd.merge(utility_data, weather_data, on='date', how='left')
    
    # Calculate heating season metrics (when HDD > 0)
    df['heating_days'] = df['HDD'] > 0
    df['cost_per_hdd'] = df.apply(
        lambda row: (row['electricity_cost'] + row['oil_cost']) / row['HDD']
        if row['HDD'] > 5  # Only calculate if we have significant heating days
        else None,
        axis=1
    )
    
    # Calculate cooling season metrics (when CDD > 0)
    df['cooling_days'] = df['CDD'] > 0
    df['cost_per_cdd'] = df.apply(
        lambda row: row['electricity_cost'] / row['CDD']
        if row['CDD'] > 5  # Only calculate if we have significant cooling days
        else None,
        axis=1
    )
    
    # Calculate total degree days and overall efficiency
    df['total_dd'] = df['HDD'] + df['CDD']
    df['cost_per_dd'] = df.apply(
        lambda row: (row['electricity_cost'] + row['oil_cost']) / row['total_dd']
        if row['total_dd'] > 5  # Only calculate if we have significant degree days
        else None,
        axis=1
    )
    
    # Fill NaN values with 0 for metrics
    df = df.fillna({
        'cost_per_hdd': 0,
        'cost_per_cdd': 0,
        'cost_per_dd': 0
    })
    
    # Debug logging for high values
    high_values = df[df['cost_per_hdd'] > 10]  # Threshold for suspicious values
    if not high_values.empty:
        logger.warning("Found unusually high cost per HDD values:")
        logger.warning(high_values[['date', 'cost_per_hdd', 'HDD', 'electricity_cost', 'oil_cost']])
    
    return df

def main():
    processed_dir = Path("data") / "processed"
    
    # Load utility and weather data
    utility_data = pd.read_csv(processed_dir / "utility_costs.csv")
    weather_data = pd.read_csv(processed_dir / "weather_data.csv", index_col=0)
    
    # Calculate efficiency metrics
    efficiency_data = calculate_efficiency_metrics(utility_data, weather_data)
    
    # Save to new CSV
    output_file = processed_dir / "efficiency_metrics.csv"
    efficiency_data.to_csv(output_file, index=False)
    logger.info(f"Efficiency metrics saved to {output_file}")

if __name__ == "__main__":
    main() 