import csv
import os
from typing import List, Dict

class CSVUtilities:
    """CSV read/write utilities. Rows are stored as dicts"""

    def __init__(self, file_path: str, fields: List[str]):
        self.file_path = file_path
        self.fields = fields
        if not self.check_file_exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}. Ensure the file exists in the correct location.")

    def check_file_exists(self) -> bool:
        return os.path.isfile(self.file_path)
    
    def read(self) -> List[Dict]:
        with open(self.file_path, mode='r', newline='') as csvfile:
            return list(csv.DictReader(csvfile))
        
    def write(self, rows: List[Dict]):
        with open(self.file_path, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(rows)

    