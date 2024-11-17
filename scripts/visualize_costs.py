import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import colorsys
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_utility_data(file_path):
    """Load utility and efficiency data from CSV files"""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter to just 2023 and 2024, and exclude future dates
    current_date = pd.Timestamp.now()
    df = df[
        (df['date'].dt.year.isin([2023, 2024])) & 
        (df['date'] <= current_date)
    ]
    
    # Add year and month columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df

def create_monthly_comparison(df, efficiency_df, normalized=False):
    """
    Create a stacked bar chart comparing monthly costs between 2023 and 2024
    normalized=True will show cost per degree day instead of total cost
    """
    plt.figure(figsize=(15, 8))
    
    # Set style
    sns.set_style("whitegrid")
    
    # Colors for each year
    colors = {
        'electricity': ['#FFD700', '#B8860B'],  # Gold, DarkGoldenrod
        'oil': ['#FF6B6B', '#8B0000']          # Light red, Dark red
    }
    
    # Set the width of each bar and positions of bars
    bar_width = 0.35
    months = range(1, 13)
    
    # Create bars for each year
    for i, year in enumerate([2023, 2024]):
        year_data = df[df['year'] == year]
        efficiency_year_data = efficiency_df[efficiency_df['date'].dt.year == year]
        
        # Calculate monthly values
        monthly_data = []
        for month in months:
            # Skip November for normalized view
            if normalized and month == 11:
                monthly_data.append({'electricity': 0, 'oil': 0, 'total': 0})
                continue
                
            month_data = year_data[year_data['month'] == month]
            month_efficiency = efficiency_year_data[efficiency_year_data['date'].dt.month == month]
            
            if not month_data.empty and not month_efficiency.empty:
                electricity = month_data['electricity_cost'].iloc[0]
                oil = month_data['oil_cost'].iloc[0]
                dd = month_efficiency['total_dd'].iloc[0]
                
                if normalized and dd > 0:
                    electricity = electricity / dd
                    oil = oil / dd
                
                monthly_data.append({
                    'electricity': electricity,
                    'oil': oil,
                    'total': electricity + oil
                })
            else:
                monthly_data.append({'electricity': 0, 'oil': 0, 'total': 0})
        
        # Position bars
        positions = [x + (i * bar_width) for x in range(len(months))]
        
        # Create stacked bars
        plt.bar(positions, 
                [m['electricity'] for m in monthly_data], 
                bar_width,
                label=f'Electricity {year}',
                color=colors['electricity'][i])
        plt.bar(positions,
                [m['oil'] for m in monthly_data],
                bar_width,
                bottom=[m['electricity'] for m in monthly_data],
                label=f'Oil {year}',
                color=colors['oil'][i])
    
    # Calculate and add difference annotations
    for month in months:
        # Skip November annotations for normalized view
        if normalized and month == 11:
            continue
            
        data_2023 = df[(df['year'] == 2023) & (df['month'] == month)]
        data_2024 = df[(df['year'] == 2024) & (df['month'] == month)]
        eff_2023 = efficiency_df[(efficiency_df['date'].dt.year == 2023) & 
                                (efficiency_df['date'].dt.month == month)]
        eff_2024 = efficiency_df[(efficiency_df['date'].dt.year == 2024) & 
                                (efficiency_df['date'].dt.month == month)]
        
        if not data_2023.empty and not data_2024.empty and not eff_2023.empty and not eff_2024.empty:
            if normalized:
                dd_2023 = eff_2023['total_dd'].iloc[0]
                dd_2024 = eff_2024['total_dd'].iloc[0]
                if dd_2023 > 0 and dd_2024 > 0:
                    total_2023 = (data_2023['electricity_cost'].iloc[0] + 
                                data_2023['oil_cost'].iloc[0]) / dd_2023
                    total_2024 = (data_2024['electricity_cost'].iloc[0] + 
                                data_2024['oil_cost'].iloc[0]) / dd_2024
                    diff = total_2024 - total_2023
                    
                    # Position the difference annotation between the bars
                    x_pos = month - 1 + bar_width
                    y_pos = max(total_2023, total_2024) + 1
                    
                    # Color code the difference
                    color = 'green' if diff < 0 else 'red'
                    plt.text(x_pos, y_pos, f'Δ ${diff:,.2f}',
                            ha='center', va='bottom', color=color,
                            fontweight='bold')
            else:
                total_2023 = data_2023['electricity_cost'].iloc[0] + data_2023['oil_cost'].iloc[0]
                total_2024 = data_2024['electricity_cost'].iloc[0] + data_2024['oil_cost'].iloc[0]
                diff = total_2024 - total_2023
                
                x_pos = month - 1 + bar_width
                y_pos = max(total_2023, total_2024) + 50
                
                color = 'green' if diff < 0 else 'red'
                plt.text(x_pos, y_pos, f'Δ ${diff:,.0f}',
                        ha='center', va='bottom', color=color,
                        fontweight='bold')
    
    # Customize the plot
    plt.xlabel('Month')
    plt.ylabel('Cost per Degree Day ($)' if normalized else 'Cost ($)')
    title = '2023 vs 2024 Monthly Cost per Degree Day' if normalized else '2023 vs 2024 Monthly Utility Costs Comparison'
    if normalized:
        title += '\n(November excluded due to incomplete degree day data)'
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Set x-axis labels to month names
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.xticks([x + bar_width/2 for x in range(len(months))], month_labels)
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    return plt

def main():
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load the data from processed directory
    processed_dir = Path("data") / "processed"
    costs_df = load_utility_data(processed_dir / "utility_costs.csv")
    efficiency_df = pd.read_csv(processed_dir / "efficiency_metrics.csv")
    efficiency_df['date'] = pd.to_datetime(efficiency_df['date'])
    
    # Create raw cost comparison
    plt = create_monthly_comparison(costs_df, efficiency_df, normalized=False)
    plt.savefig(output_dir / 'utility_comparison.png', bbox_inches='tight')
    plt.close()
    
    # Create normalized cost comparison
    plt = create_monthly_comparison(costs_df, efficiency_df, normalized=True)
    plt.savefig(output_dir / 'utility_comparison_normalized.png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main() 