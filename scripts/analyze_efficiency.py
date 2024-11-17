import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_efficiency_data(file_path: Path) -> pd.DataFrame:
    """Load and prepare efficiency data for analysis"""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter to last 24 months
    latest_date = df['date'].max()
    cutoff_date = latest_date - pd.DateOffset(months=23)
    df = df[df['date'] >= cutoff_date]
    
    # Add year and month for grouping
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    return df

def create_efficiency_comparison(df: pd.DataFrame) -> plt.Figure:
    """Create comparison plots of normalized energy costs"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Set style using seaborn
    sns.set_style("whitegrid")
    
    # Colors for different years
    years = sorted(df['year'].unique())
    colors = sns.color_palette("husl", len(years))
    
    # Plot 1: Cost per Heating Degree Day
    for year, color in zip(years, colors):
        year_data = df[df['year'] == year]
        ax1.plot(year_data['month'], year_data['cost_per_hdd'], 
                marker='o', label=str(year), color=color)
    
    ax1.set_title('Cost per Heating Degree Day by Month')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Cost per HDD ($)')
    ax1.set_xticks(range(1, 13))
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Cost per Total Degree Day
    for year, color in zip(years, colors):
        year_data = df[df['year'] == year]
        ax2.plot(year_data['month'], year_data['cost_per_dd'], 
                marker='o', label=str(year), color=color)
    
    ax2.set_title('Cost per Total Degree Day by Month')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Cost per Degree Day ($)')
    ax2.set_xticks(range(1, 13))
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    return plt

def calculate_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate summary statistics for efficiency metrics"""
    # Group by year and calculate stats
    yearly_stats = df.groupby('year').agg({
        'cost_per_hdd': ['mean', 'std', 'min', 'max'],
        'cost_per_dd': ['mean', 'std', 'min', 'max'],
        'HDD': 'sum',
        'CDD': 'sum',
        'electricity_cost': 'sum',
        'oil_cost': 'sum'
    }).round(2)
    
    # Calculate total costs
    yearly_stats['total_cost'] = (
        yearly_stats[('electricity_cost', 'sum')] + 
        yearly_stats[('oil_cost', 'sum')]
    )
    
    # Calculate cost per degree day for the whole year
    yearly_stats['annual_cost_per_dd'] = (
        yearly_stats['total_cost'] / 
        (yearly_stats[('HDD', 'sum')] + yearly_stats[('CDD', 'sum')])
    ).round(2)
    
    return yearly_stats

def main():
    # Setup paths
    processed_dir = Path("data") / "processed"
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load efficiency data
    logger.info("Loading efficiency data...")
    df = load_efficiency_data(processed_dir / "efficiency_metrics.csv")
    
    # Debug logging
    logger.info(f"Data loaded with {len(df)} records")
    logger.info(f"Columns available: {df.columns.tolist()}")
    logger.info(f"Sample of HDD/CDD data:\n{df[['date', 'HDD', 'CDD']].head()}")
    
    # Create visualization
    plt = create_efficiency_comparison(df)
    plt.savefig(output_dir / 'efficiency_comparison.png', bbox_inches='tight')
    plt.close()
    
    # Calculate and save summary statistics
    yearly_stats = calculate_summary_stats(df)
    yearly_stats.to_csv(output_dir / 'efficiency_summary.csv')
    
    # Log summary information
    logger.info("\nEfficiency Summary by Year:")
    logger.info(f"\n{yearly_stats}")

if __name__ == "__main__":
    main() 