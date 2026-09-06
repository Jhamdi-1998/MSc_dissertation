"""
config.py: Here are all the fixed parameters used with our data..

--
Pairs:
Just to avoid getting confused: the order of the stock in the pairs will be kept in the same order
as the written methodology (OLS for example)
"""

PAIRS = [
    ("KO", "PEP"),
    ("F", "GM"),
    ("UAL", "DAL"),
    ("JPM", "BAC"),
    ("MSFT", "ORCL"),
    ("ADP", "FISV"),
]

# Sector labels
SECTOR_MAP = {
    "KO": "Beverages",
    "PEP": "Beverages",
    "F": "Automobile",
    "GM": "Automobile",
    "UAL": "Airlines",
    "DAL": "Airlines",
    "JPM": "Banking",
    "BAC": "Banking",
    "MSFT": "Technology",
    "ORCL": "Technology",
    "ADP": "Data",
    "FISV": "Data",
}

# Company OFFICIAL names
COMPANY_NAMES = {
    "KO": "The Coca-Cola Company",
    "PEP": "PepsiCo, Inc.",
    "F": "Ford Motor Company",
    "GM": "General Motors Company",
    "UAL": "United Airlines Holdings, Inc.",
    "DAL": "Delta Air Lines, Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "BAC": "Bank of America Corporation",
    "MSFT": "Microsoft Corporation",
    "ORCL": "Oracle Corporation",
    "ADP": "Automatic Data Processing, Inc.",
    "FISV": "Fiserv, Inc.",
}

# Building a list of the tickers, from "PAIRS"
ALL_TICKERS = sorted({ticker for pair in PAIRS for ticker in pair})

# Formation and trading periods
FORMATION_START = "2021-01-01"
FORMATION_END = "2021-12-31"

TRADING_START = "2022-01-01"
TRADING_END = "2022-12-31"

# To extract data we need to pull the full period (formation + trading)
PULL_START = FORMATION_START
PULL_END = TRADING_END

# File paths
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
TABLES_DIR = "outputs/tables"
FIGURES_DIR = "outputs/figures"