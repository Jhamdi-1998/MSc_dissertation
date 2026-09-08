"""
config.py: Here are all the fixed parameters used with our data..

--
Pairs:
Just to avoid getting confused: the order of the stock in the pairs will be kept in the same order
as the written methodology (OLS for example)
"""

PAIRS = [
    ("DTE", "AEP"),
    ("KIM", "O"),
    ("T", "VZ"),
    ("UNH", "CVS"),
    ("HD", "LOW"),
    ("JPM", "BAC"),
]

# Sector labels
SECTOR_MAP = {
    "DTE": "Utilities",
    "AEP": "Utilities",
    "KIM": "Real Estate",
    "O": "Real Estate",
    "T": "Communication Services",
    "VZ": "Communication Services",
    "UNH": "Healthcare",
    "CVS": "Healthcare",
    "HD": "Non-essential goods",
    "LOW": "Non-essential goods",
    "JPM": "Banking",
    "BAC": "Banking",
}

# Company OFFICIAL names
COMPANY_NAMES = {
"DTE": "DTE Energy Company",
    "AEP": "American Electric Power Company, Inc.",
    "KIM": "Kimco Realty Corporation",
    "O": "Realty Income Corporation",
    "T": "AT&T Inc.",
    "VZ": "Verizon Communications Inc.",
    "UNH": "UnitedHealth Group Incorporated",
    "CVS": "CVS Health Corporation",
    "HD": "The Home Depot, Inc.",
    "LOW": "Lowe's Companies, Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "BAC": "Bank of America Corporation",
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