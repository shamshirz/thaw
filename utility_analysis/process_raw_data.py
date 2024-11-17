import pandas as pd
from pathlib import Path
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_rate(amount: float, usage: Optional[float]) -> Optional[float]:
    """Calculate rate per unit ($/kwh or $/gallon)"""
    if pd.isna(usage) or usage == 0:
        return None
    return amount / usage

def process_electric_data(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process raw electric bill data and group by month.
    Returns: (monthly costs DataFrame, monthly rates DataFrame)
    """
    logger.info(f"Processing electric data from {file_path}")
    df = pd.read_csv(file_path)
    # Parse YYYY-MM format and set to first day of month
    df['date'] = pd.to_datetime(df['date'] + '-01')
    
    # Calculate rates where possible
    df['rate'] = df.apply(lambda row: calculate_rate(row['amount'], row['kwh_used']), axis=1)
    
    # Data is already monthly, no need to group
    monthly_costs = df[['date', 'amount']].copy()
    monthly_rates = df[['date', 'rate', 'kwh_used']].copy()
    
    return monthly_costs, monthly_rates

def process_oil_data(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process raw oil delivery data and group by month.
    Returns: (monthly costs DataFrame, monthly rates DataFrame)
    """
    logger.info(f"Processing oil data from {file_path}")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate rates where possible
    df['rate'] = df.apply(lambda row: calculate_rate(row['amount'], row['gallons']), axis=1)
    
    # Group by month for costs
    monthly_costs = df.groupby(df['date'].dt.to_period('M')).agg({
        'amount': 'sum',
        'gallons': 'sum'
    }).reset_index()
    
    # Calculate monthly rates where possible
    monthly_rates = monthly_costs.copy()
    monthly_rates['rate'] = monthly_rates.apply(
        lambda row: calculate_rate(row['amount'], row['gallons']), 
        axis=1
    )
    
    # Convert period to datetime for the first of each month
    monthly_costs['date'] = monthly_costs['date'].dt.to_timestamp()
    monthly_rates['date'] = monthly_rates['date'].dt.to_timestamp()
    
    return monthly_costs[['date', 'amount']], monthly_rates[['date', 'rate', 'gallons']]

def combine_utility_data(electric_df: pd.DataFrame, oil_df: pd.DataFrame) -> pd.DataFrame:
    """Combine electric and oil cost data into a single DataFrame"""
    logger.info("Combining utility cost data")
    
    # Create a date range covering all dates
    all_dates = pd.concat([electric_df['date'], oil_df['date']])
    date_range = pd.date_range(
        start=all_dates.min().replace(day=1),
        end=all_dates.max().replace(day=1),
        freq='MS'
    )
    
    # Create a DataFrame with all months
    combined = pd.DataFrame({'date': date_range})
    
    # Rename columns before merging to avoid suffix confusion
    electric_df = electric_df.rename(columns={'amount': 'electricity_cost'})
    oil_df = oil_df.rename(columns={'amount': 'oil_cost'})
    
    # Merge electric and oil data
    combined = combined.merge(
        electric_df[['date', 'electricity_cost']], 
        on='date', 
        how='left'
    ).merge(
        oil_df[['date', 'oil_cost']], 
        on='date', 
        how='left'
    )
    
    # Fill missing values with 0
    combined = combined.fillna(0)
    
    return combined[['date', 'electricity_cost', 'oil_cost']]

def save_rate_data(electric_rates: pd.DataFrame, oil_rates: pd.DataFrame, output_dir: Path):
    """Save rate information to separate CSV files"""
    logger.info("Saving rate data")
    
    # Save electric rates
    electric_rates.to_csv(output_dir / 'electric_rates.csv', index=False)
    logger.info(f"Electric rates saved to {output_dir / 'electric_rates.csv'}")
    
    # Save oil rates
    oil_rates.to_csv(output_dir / 'oil_rates.csv', index=False)
    logger.info(f"Oil rates saved to {output_dir / 'oil_rates.csv'}")

def main():
    data_dir = Path("data")
    electric_raw = data_dir / "electric_raw.csv"
    oil_raw = data_dir / "oil_raw.csv"
    
    # Process each utility's data
    electric_costs, electric_rates = process_electric_data(electric_raw)
    oil_costs, oil_rates = process_oil_data(oil_raw)
    
    # Combine the cost data
    combined_df = combine_utility_data(electric_costs, oil_costs)
    
    # Save the combined cost data
    combined_df.to_csv(data_dir / "utility_costs.csv", index=False)
    logger.info(f"Combined utility data saved to {data_dir / 'utility_costs.csv'}")
    
    # Save the rate data
    save_rate_data(electric_rates, oil_rates, data_dir)

if __name__ == "__main__":
    main() 