import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_utility_data(file_path):
    """
    Load utility data from CSV file.
    Expected CSV format:
    date,electricity_cost,oil_cost
    2022-01-01,100.50,200.75
    """
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df

def create_monthly_comparison(df):
    """
    Create a stacked bar chart comparing monthly costs across years
    with electricity in yellow and oil in red
    """
    plt.figure(figsize=(15, 7))
    
    # Get unique years for comparison
    years = sorted(df['year'].unique())
    
    # Set the width of each bar and positions of bars
    bar_width = 0.35
    months = range(1, 13)
    
    # Color schemes for each year
    colors = {
        'electricity': ['#FFE5B4', '#FFD700'],  # Light yellow to golden yellow
        'oil': ['#FF6B6B', '#8B0000']          # Light red to dark red
    }
    
    # Create bars for each year
    for i, year in enumerate(years):
        year_data = df[df['year'] == year]
        
        # Calculate monthly costs
        monthly_electricity = [
            year_data[year_data['month'] == month]['electricity_cost'].iloc[0] 
            if not year_data[year_data['month'] == month].empty 
            else 0 
            for month in months
        ]
        
        monthly_oil = [
            year_data[year_data['month'] == month]['oil_cost'].iloc[0] 
            if not year_data[year_data['month'] == month].empty 
            else 0 
            for month in months
        ]
        
        # Position bars
        positions = [x + (i * bar_width) for x in range(len(months))]
        
        # Create stacked bars
        plt.bar(positions, monthly_electricity, bar_width, 
                label=f'Electricity {year}', 
                color=colors['electricity'][i])
        plt.bar(positions, monthly_oil, bar_width, 
                bottom=monthly_electricity,
                label=f'Oil {year}', 
                color=colors['oil'][i])
    
    # Customize the plot
    plt.xlabel('Month')
    plt.ylabel('Cost ($)')
    plt.title('Monthly Utility Costs Comparison by Year')
    plt.legend()
    
    # Set x-axis labels to month names
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.xticks([x + bar_width/2 for x in range(len(months))], month_labels)
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    return plt

def main():
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Load the data
    file_path = Path("data") / "utility_costs.csv"
    df = load_utility_data(file_path)
    
    # Create combined plot
    plt = create_monthly_comparison(df)
    plt.savefig(output_dir / 'utility_comparison.png')
    plt.close()

if __name__ == "__main__":
    main() 