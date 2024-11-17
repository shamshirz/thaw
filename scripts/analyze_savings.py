import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_monthly_savings(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly savings comparing 2024 to 2023"""
    # Filter for just 2023 and 2024
    df_2023 = df[df['date'].dt.year == 2023].copy()
    df_2024 = df[df['date'].dt.year == 2024].copy()
    
    # Ensure we're comparing same months
    months = sorted(set(df_2023['date'].dt.month) & set(df_2024['date'].dt.month))
    
    savings_data = []
    running_total = 0
    
    for month in months:
        data_2023 = df_2023[df_2023['date'].dt.month == month].iloc[0]
        data_2024 = df_2024[df_2024['date'].dt.month == month].iloc[0]
        
        # Calculate total cost difference
        cost_2023 = data_2023['electricity_cost'] + data_2023['oil_cost']
        cost_2024 = data_2024['electricity_cost'] + data_2024['oil_cost']
        monthly_savings = cost_2023 - cost_2024
        
        # Calculate degree day adjusted savings
        dd_2023 = data_2023['HDD'] + data_2023['CDD']
        dd_2024 = data_2024['HDD'] + data_2024['CDD']
        
        # Normalize savings by degree days if available
        if dd_2023 > 0 and dd_2024 > 0:
            normalized_savings = (cost_2023/dd_2023 - cost_2024/dd_2024) * dd_2024
        else:
            normalized_savings = monthly_savings
        
        running_total += monthly_savings
        
        savings_data.append({
            'month': month,
            'monthly_savings': monthly_savings,
            'normalized_savings': normalized_savings,
            'running_total': running_total,
            'degree_days_2023': dd_2023,
            'degree_days_2024': dd_2024
        })
    
    return pd.DataFrame(savings_data)

def create_savings_visualization(savings_df: pd.DataFrame) -> plt.Figure:
    """Create visualization comparing 2024 to 2023 costs"""
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # Set style
    sns.set_style("whitegrid")
    
    # Plot bars for monthly savings
    bars = ax1.bar(savings_df['month'], savings_df['normalized_savings'], 
                   color=sns.color_palette("RdYlGn", len(savings_df)),
                   alpha=0.7)
    
    # Create second y-axis for running total
    ax2 = ax1.twinx()
    ax2.plot(savings_df['month'], savings_df['running_total'], 
             color='darkblue', linewidth=2, marker='o')
    
    # Customize the plot
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Monthly Savings vs 2023 ($)')
    ax2.set_ylabel('Running Total Savings ($)')
    
    # Set x-axis labels to month names
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Only use the months we have data for
    available_months = sorted(savings_df['month'].unique())
    ax1.set_xticks(available_months)
    ax1.set_xticklabels([month_labels[m-1] for m in available_months])
    
    # Add title
    plt.title('2024 Cost Savings Compared to 2023\n(Normalized by Degree Days)', 
             pad=20)
    
    # Add zero line
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., 
                height if height > 0 else height - 20,
                f'${abs(height):.0f}',
                ha='center', va='bottom' if height > 0 else 'top')
    
    # Adjust layout
    plt.tight_layout()
    
    return plt

def main():
    # Setup paths
    processed_dir = Path("data") / "processed"
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load efficiency data
    df = pd.read_csv(processed_dir / "efficiency_metrics.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate savings
    savings_df = calculate_monthly_savings(df)
    
    # Create visualization
    plt = create_savings_visualization(savings_df)
    plt.savefig(output_dir / 'savings_analysis.png', bbox_inches='tight')
    plt.close()
    
    # Save detailed savings data
    savings_df.to_csv(output_dir / 'monthly_savings.csv', index=False)
    
    # Log summary
    total_savings = savings_df['monthly_savings'].sum()
    normalized_savings = savings_df['normalized_savings'].sum()
    logger.info(f"\nSavings Summary (2024 vs 2023):")
    logger.info(f"Total Raw Savings: ${total_savings:.2f}")
    logger.info(f"Total Normalized Savings: ${normalized_savings:.2f}")

if __name__ == "__main__":
    main() 