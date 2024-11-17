import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def create_monthly_comparison(df, utility_type):
    """
    Create a grouped bar chart comparing monthly costs across years
    utility_type: 'electricity_cost' or 'oil_cost'
    """
    plt.figure(figsize=(15, 7))
    
    # Get unique years for comparison
    years = sorted(df['year'].unique())
    
    # Set the width of each bar and positions of bars
    bar_width = 0.35
    months = range(1, 13)
    
    # Create bars for each year
    for i, year in enumerate(years):
        year_data = df[df['year'] == year]
        monthly_costs = [
            year_data[year_data['month'] == month][utility_type].iloc[0] 
            if not year_data[year_data['month'] == month].empty 
            else 0 
            for month in months
        ]
        
        positions = [x + (i * bar_width) for x in range(len(months))]
        plt.bar(positions, monthly_costs, bar_width, label=str(year))
    
    # Customize the plot
    plt.xlabel('Month')
    plt.ylabel('Cost ($)')
    plt.title(f'Monthly {utility_type.replace("_", " ").title()} Comparison by Year')
    plt.legend()
    
    # Set x-axis labels to month names
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.xticks([x + bar_width/2 for x in range(len(months))], month_labels)
    
    # Add grid for better readability
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    return plt

def main():
    # Load the data
    file_path = 'utility_costs.csv'
    df = load_utility_data(file_path)
    
    # Create plots for both electricity and oil
    create_monthly_comparison(df, 'electricity_cost')
    plt.savefig('electricity_comparison.png')
    plt.close()
    
    create_monthly_comparison(df, 'oil_cost')
    plt.savefig('oil_comparison.png')
    plt.close()

if __name__ == "__main__":
    main() 