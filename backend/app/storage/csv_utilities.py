import csv
import os
from pathlib import Path
from typing import List, Dict

class CSVUtilities:
    """CSV read/write utilities. Rows are stored as dicts"""

    def __init__(self, file_path: str, fields: List[str]):
        self.file_path = Path(file_path)
        self.fields = fields
        if not self._check_file_exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}. Ensure the file exists in the correct location.")

    def _check_file_exists(self) -> bool:
        return self.file_path.is_file()
    
    def read_all(self) -> List[Dict]:
        with open(self.file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            return list(csv.DictReader(csvfile))
        
    def write_all(self, rows: List[Dict]):
        tmp = self.file_path.with_suffix(".tmp")
        with open(tmp, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp, self.file_path)
    

    