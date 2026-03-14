"""Parse encounter date from folder name."""
import re
from datetime import datetime

def parse_encounter_date(folder_name: str) -> str | None:
    """
    Parse encounter date from folder name like '019M72177_N991-796129_20241213'.
    Returns ISO date string 'YYYY-MM-DD' or None.
    """
    # Try to find YYYYMMDD pattern at end of folder name
    match = re.search(r'(\d{8})$', folder_name)
    if match:
        date_str = match.group(1)
        try:
            dt = datetime.strptime(date_str, '%Y%m%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Try to find date elsewhere in the name
    match = re.search(r'(\d{4})(\d{2})(\d{2})', folder_name)
    if match:
        try:
            dt = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    return None
