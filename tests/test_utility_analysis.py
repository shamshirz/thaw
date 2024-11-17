import pandas as pd
from pathlib import Path
import pytest
import matplotlib.pyplot as plt
from utility_analysis import create_monthly_comparison, load_utility_data

@pytest.fixture
def sample_data():
    """Create sample utility data for testing"""
    data = {
        'date': pd.date_range(start='2022-01-01', end='2023-12-31', freq='MS'),
        'electricity_cost': [100 + i % 50 for i in range(24)],  # Creates varying costs
        'oil_cost': [200 + i % 75 for i in range(24)]  # Creates varying costs
    }
    df = pd.DataFrame(data)
    # Add year and month columns that the visualization function expects
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df

def test_load_utility_data(tmp_path):
    """Test that utility data loads correctly"""
    # Create a temporary CSV file
    test_csv = tmp_path / "test_utility_costs.csv"
    sample_df = pd.DataFrame({
        'date': ['2022-01-01', '2022-02-01'],
        'electricity_cost': [100, 110],
        'oil_cost': [200, 210]
    })
    sample_df.to_csv(test_csv, index=False)
    
    # Load and verify the data
    df = load_utility_data(test_csv)
    assert len(df) == 2
    assert 'year' in df.columns
    assert 'month' in df.columns

def test_create_monthly_comparison(sample_data, tmp_path):
    """Test that visualization is created successfully"""
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Test combined visualization
    plt = create_monthly_comparison(sample_data)
    plt.savefig(output_dir / 'test_utility_comparison.png')
    plt.close()
    
    assert (output_dir / 'test_utility_comparison.png').exists() 