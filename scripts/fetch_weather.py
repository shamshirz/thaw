import pandas as pd
from pathlib import Path
import logging
from meteostat import Point, Daily
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDataFetcher:
    def __init__(self, latitude: float, longitude: float, base_temp_c: float = 18.0):
        """
        Initialize weather data fetcher
        Args:
            latitude: Location latitude
            longitude: Location longitude
            base_temp_c: Base temperature for HDD/CDD calculation (Celsius)
        """
        self.location = Point(latitude, longitude)
        self.base_temp = base_temp_c
        
    def fetch_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch weather data for given date range"""
        logger.info(f"Fetching weather data from {start_date} to {end_date}")
        
        # Fetch daily weather data
        weather_data = Daily(self.location, start_date, end_date)
        df = weather_data.fetch()
        
        if df.empty:
            raise ValueError("No weather data retrieved")
        
        return df
    
    def calculate_degree_days(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Heating and Cooling Degree Days"""
        # Calculate HDD
        df['HDD'] = self.base_temp - df['tavg']
        df['HDD'] = df['HDD'].apply(lambda x: x if x > 0 else 0)
        
        # Calculate CDD
        df['CDD'] = df['tavg'] - self.base_temp
        df['CDD'] = df['CDD'].apply(lambda x: x if x > 0 else 0)
        
        return df
    
    def process_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate data to monthly values"""
        monthly = df.resample('M').agg({
            'tavg': 'mean',
            'tmin': 'min',
            'tmax': 'max',
            'prcp': 'sum',
            'snow': 'sum',
            'HDD': 'sum',
            'CDD': 'sum'
        })
        
        return monthly

def load_config() -> dict:
    """Load configuration from config file"""
    config_path = Path("config.json")
    if not config_path.exists():
        raise FileNotFoundError(
            "config.json not found. Please create one with your location details."
        )
    
    with open(config_path) as f:
        return json.load(f)

def get_date_range() -> tuple[datetime, datetime]:
    """Get date range from utility data"""
    utility_costs = pd.read_csv(Path("data") / "processed" / "utility_costs.csv")
    utility_costs['date'] = pd.to_datetime(utility_costs['date'])
    
    start_date = utility_costs['date'].min()
    end_date = utility_costs['date'].max()
    
    return start_date, end_date

def main():
    # Load configuration
    config = load_config()
    
    # Setup paths
    processed_dir = Path("data") / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    # Initialize weather fetcher
    fetcher = WeatherDataFetcher(
        latitude=config['latitude'],
        longitude=config['longitude'],
        base_temp_c=config.get('base_temp_c', 18.0)
    )
    
    # Get date range from utility data
    start_date, end_date = get_date_range()
    
    # Fetch and process weather data
    try:
        weather_data = fetcher.fetch_data(start_date, end_date)
        weather_data = fetcher.calculate_degree_days(weather_data)
        monthly_data = fetcher.process_monthly(weather_data)
        
        # Save processed data
        output_file = processed_dir / "weather_data.csv"
        monthly_data.to_csv(output_file)
        logger.info(f"Weather data saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing weather data: {e}")
        raise

if __name__ == "__main__":
    main() 