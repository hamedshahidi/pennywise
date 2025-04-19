"""
Bank report import module for processing CSV and Excel files.
"""
import pandas as pd
from pathlib import Path
from typing import Union, Literal
from datetime import datetime

# Column name mappings from Finnish to English
COLUMN_MAPPINGS = {
    'Kirjauspäivä': 'posting_date',
    'Maksupäivä': 'payment_date',
    'Summa': 'amount',
    'Tapahtumalaji': 'transaction_type',
    'Maksaja': 'payer',
    'Saajan nimi': 'recipient_name',
    'Saajan tilinumero': 'recipient_account',
    'Saajan BIC-tunnus': 'recipient_bic',
    'Viitenumero': 'reference_number',
    'Viesti': 'message',
    'Arkistointitunnus': 'archive_id'
}

def clean_amount(amount_str: str) -> float:
    """Convert Finnish formatted amount string to float."""
    # Remove any spaces and replace comma with dot
    cleaned = amount_str.strip().replace(',', '.')
    # Convert to float (the +/- prefix will be handled automatically)
    return float(cleaned)

def parse_finnish_date(date_str: str) -> datetime:
    """Convert Finnish date format (DD.MM.YYYY) to datetime."""
    return datetime.strptime(date_str.strip(), '%d.%m.%Y')

def import_bank_report(
    file_path: Union[str, Path],
    source_type: Literal["CSV", "Manual"] = "CSV"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Import bank report from CSV or Excel file and split into income and expenses.
    
    Args:
        file_path: Path to the CSV or Excel file
        source_type: Source of the data, either "CSV" or "Manual"
        
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Income and expenses dataframes
    """
    # Convert string path to Path object
    file_path = Path(file_path)
    
    # Read file based on extension
    if file_path.suffix.lower() == '.csv':
        # Read with specific Finnish CSV format settings
        df = pd.read_csv(
            file_path,
            sep=';',  # Finnish CSV uses semicolon separator
            encoding='utf-8',
            # Don't use pandas' number parsing - we'll do it manually
            dtype=str,  # Read all columns as strings initially
        )
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, dtype=str)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Normalize column names to English
    df = df.rename(columns=COLUMN_MAPPINGS)
    
    # Clean and convert data types
    df['amount'] = df['amount'].apply(clean_amount)
    df['posting_date'] = df['posting_date'].apply(parse_finnish_date)
    df['payment_date'] = df['payment_date'].apply(parse_finnish_date)
    
    # Add source tag
    df['source'] = source_type
    
    # Split into income and expenses based on amount
    income_df = df[df['amount'] > 0].copy()
    expenses_df = df[df['amount'] < 0].copy()
    
    # Make expenses positive for easier calculations
    expenses_df['amount'] = expenses_df['amount'].abs()
    
    return income_df, expenses_df

def get_transaction_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary of transactions by type.
    
    Args:
        df: DataFrame containing transactions
        
    Returns:
        DataFrame with transaction type summaries
    """
    return df.groupby('transaction_type').agg({
        'amount': ['count', 'sum'],
        'posting_date': ['min', 'max']
    }).round(2) 