"""
Filename parser for multi-account, multi-month CSV imports.
Now supports underscore format: <person>_<account>_<YYYY>_<MM>.csv
"""

import re
from typing import Optional


def parse_filename(filename: str) -> Optional[dict]:
    """
    Parses filenames like 'alice_saving_2024_03.csv' and returns components.

    Returns:
        dict or None if filename doesn't match expected format:
        {
            'person': 'alice',
            'account': 'saving',
            'year': 2024,
            'month': 3,
            'year_month': '2024-03'
        }
    """
    pattern = r"^([a-z]+)_([a-z]+)_(\d{4})_(\d{2})\.csv$"
    match = re.match(pattern, filename.lower())
    if not match:
        return None

    return {
        'person': match.group(1),
        'account': match.group(2),
        'year': int(match.group(3)),
        'month': int(match.group(4)),
        'year_month': f"{match.group(3)}-{match.group(4)}"
    }
