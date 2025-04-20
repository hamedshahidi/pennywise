"""
Transaction categorization module for automatic expense classification.
"""
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
import json

# Default category mappings (can be extended via JSON config)
DEFAULT_CATEGORY_MAPPINGS = {
    "food": [
        "LIDL", "K-MARKET", "K MARKET", "S-MARKET", "ALEPA", "PRISMA",
        "CITYMARKET", "SALE", "TOKMANNI", "RUOHONJUURI"
    ],
    "transport": [
        "HSL", "VR", "FINNAIR", "NORWEGIAN", "TAXI", "TAKSI",
        "UBER", "BOLT.EU", "VANTAAN TAKSI", "LÄHITAKSI"
    ],
    "utilities": [
        "HELEN", "VANTAAN ENERGIA", "CARUNA", "HSY", "DNA OYJ",
        "ELISA", "TELIA", "FORTUM"
    ],
    "entertainment": [
        "NETFLIX", "SPOTIFY", "HBO", "ELOKUVA", "FINNKINO", "ZYNGA",
        "STEAM", "SUPERCELL", "NINTENDO", "PLAYSTATION"
    ],
    "health": [
        "APTEEKKI", "YLIOPISTON APTEEKKI", "MEHILÄINEN", "TERVEYSTALO",
        "AAVA", "HAMMASLÄÄKÄRI", "FYSIOS", "HOITO"
    ],
    "rent": [
        "VUOKRA", "VUOKRANANTAJA", "SATO", "LUMO", "KOJAMO", "ASUNTO OY",
        "RENTAL", "MAANVUOKRA"
    ]
}

def load_category_mappings(config_path: Optional[Path] = None) -> Dict[str, List[str]]:
    """
    Load category mappings from a JSON file or use defaults.
    
    Args:
        config_path: Optional path to JSON config file with category mappings
        
    Returns:
        Dictionary mapping categories to lists of keywords
    """
    if config_path and config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CATEGORY_MAPPINGS

def categorize_transaction(
    description: str,
    amount: float,
    mappings: Dict[str, List[str]]
) -> str:
    """
    Categorize a single transaction based on its description and amount.
    
    Args:
        description: Transaction description or recipient name
        amount: Transaction amount
        mappings: Dictionary of category mappings
        
    Returns:
        Category name or "uncategorized" if no match found
    """
    description = description.upper()
    
    # Check each category's keywords
    for category, keywords in mappings.items():
        if any(keyword.upper() in description for keyword in keywords):
            return category
            
    return "uncategorized"

def categorize_transactions(
    df: pd.DataFrame,
    mappings: Optional[Dict[str, List[str]]] = None,
    description_column: str = "recipient_name",
    amount_column: str = "amount"
) -> pd.DataFrame:
    """
    Categorize all transactions in a DataFrame.
    
    Args:
        df: DataFrame containing transactions
        mappings: Optional custom category mappings
        description_column: Name of the column containing transaction descriptions
        amount_column: Name of the column containing transaction amounts
        
    Returns:
        DataFrame with added 'category' and 'auto_categorized' columns
    """
    if mappings is None:
        mappings = DEFAULT_CATEGORY_MAPPINGS
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Add category column
    result_df["category"] = result_df[description_column].apply(
        lambda x: categorize_transaction(str(x), 0, mappings)
    )
    
    # Add flag for auto-categorization
    result_df["auto_categorized"] = True
    
    return result_df

def save_categorized_data(
    df: pd.DataFrame,
    output_path: Path,
    format: str = "csv"
) -> None:
    """
    Save categorized transactions to a file.
    
    Args:
        df: DataFrame containing categorized transactions
        output_path: Path to save the file
        format: Output format ("csv" or "json")
    """
    output_path = Path(output_path)
    
    if format.lower() == "csv":
        df.to_csv(output_path, index=False, encoding="utf-8")
    elif format.lower() == "json":
        df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")

def override_category(
    df: pd.DataFrame,
    index: int,
    new_category: str
) -> pd.DataFrame:
    """
    Override the auto-assigned category for a specific transaction.
    
    Args:
        df: DataFrame containing categorized transactions
        index: Index of the transaction to update
        new_category: New category to assign
        
    Returns:
        Updated DataFrame
    """
    df = df.copy()
    df.loc[index, "category"] = new_category
    df.loc[index, "auto_categorized"] = False
    return df 