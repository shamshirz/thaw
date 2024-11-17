# Utility Analysis

A tool for analyzing and visualizing utility costs over time.

## Setup

### Project Setup

Install Python and dependencies using mise and poetry:
```bash
mise install
poetry install
poetry run pytest
```

## Usage

1. Place your utility cost data in `data/utility_costs.csv` with the following format:

```csv
date,electricity_cost,oil_cost
2022-01-01,145.50,250.75
2022-02-01,132.25,225.50
```

2. Run the analysis:
```bash
poetry run ua
```

The script will generate two visualization files in the `output` directory:
- `electricity_comparison.png`
- `oil_comparison.png`

## Verify Installation

Run the test suite to verify everything is working correctly:
```bash
poetry run pytest
```

This will run a simple test that generates visualizations using sample data. If successful, you'll see test output and sample charts in the `output` directory.

### Prerequisites

1. Install [mise](https://mise.jdx.dev/getting-started.html) for managing Python versions:

```bash
curl https://mise.run | sh
```

2. Install Poetry for dependency management:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Data Processing

If you have raw utility data, you can process it using the following steps:

1. Place your raw data files in the `data` directory:
   - `electric_raw.csv`: Electric bill data with columns: date, amount, kwh_used, rate
   - `oil_raw.csv`: Oil delivery data with columns: date, amount, gallons, price_per_gallon

2. Process the raw data:
```bash
poetry run process
```

This will create `utility_costs.csv` in the data directory, which can then be used by the main analysis script.

## PDF Bill Processing - Under Development

To extract data from PDF bills:

1. Place your electric bill PDFs in `data/electric_bills/`
2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the extraction:
```bash
poetry run extract
```

This will create `electric_raw.csv` from your PDF bills.