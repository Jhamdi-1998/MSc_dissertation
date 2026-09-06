"""
config.py:
Here are all the fixed parameters used with our data.
No other script should be used, it sould be imported from here.
"""
"""
Pairs:
Each pair is (Stock A, Stock B) as they'll appear in the Engle-Granger
regression: log P_A,t = alpha + beta * log P_B,t + eps_t
Order follows the Section 5.3.1 of the paper.
"""

PAIRS = [
    ("KO", "PEP"),     # Coca-Cola / PepsiCo - Beverages
    ("F", "GM"),       # Ford / General Motors - Automobile
    ("UAL", "DAL"),    # United Airlines / Delta Air Lines - Airlines
    ("JPM", "BAC"),    # JPMorgan Chase / Bank of America - Banking
    ("MSFT", "ORCL"),  # Microsoft / Oracle - Technology
    ("ADP", "FI"),     # Automatic Data Processing / Fiserv - Data
]

# Sector labels for the company description table (Section 7.1.1)
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
    "FI": "Data",
}

# Full company names for the description table
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
    "FI": "Fiserv, Inc.",
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