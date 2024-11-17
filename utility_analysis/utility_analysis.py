import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import colorsys
from datetime import datetime

def load_utility_data(file_path):
    """
    Load utility data from CSV file and filter to last 24 months.
    Expected CSV format:
    date,electricity_cost,oil_cost
    2022-01-01,100.50,200.75
    """
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter to last 24 months
    latest_date = df['date'].max()
    cutoff_date = latest_date - pd.DateOffset(months=23)  # 24 months including latest
    df = df[df['date'] >= cutoff_date]
    
    # Add year and month columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df

def generate_color_gradient(base_color: tuple[float, float, float], num_years: int) -> list[str]:
    """Generate a list of colors from light to dark versions of the base color"""
    colors = []
    for i in range(num_years):
        # Adjust brightness while keeping hue and saturation
        h, s, v = colorsys.rgb_to_hsv(*base_color)
        # Start brighter and get darker with each year
        v = max(0.3, 1.0 - (i * 0.2))  # Limit darkness to 0.3
        rgb = colorsys.hsv_to_rgb(h, s, v)
        # Convert to hex color code
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255), 
            int(rgb[1] * 255), 
            int(rgb[2] * 255)
        )
        colors.append(hex_color)
    return colors

def create_monthly_comparison(df):
    """
    Create a stacked bar chart comparing monthly costs across years
    with electricity in yellow and oil in red
    """
    plt.figure(figsize=(15, 7))
    
    # Get unique years for comparison
    years = sorted(df['year'].unique())
    num_years = len(years)
    
    # Generate color schemes for each utility type
    colors = {
        'electricity': generate_color_gradient((1.0, 0.84, 0.0), num_years),  # Golden yellow base
        'oil': generate_color_gradient((0.8, 0.0, 0.0), num_years)           # Red base
    }
    
    # Set the width of each bar and positions of bars
    bar_width = 0.35
    months = range(1, 13)
    
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
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Set x-axis labels to month names
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.xticks([x + (bar_width * (num_years - 1) / 2) for x in range(len(months))], 
               month_labels)
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
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
    plt.savefig(output_dir / 'utility_comparison.png', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main() 