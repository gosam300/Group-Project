"""
File I/O and Storage Module

Handles saving and loading record data to/from a JSON file.
Keeps records in memory during the program and writes to disk on save.

Key concepts:
    - Serialization: Converting Python data to JSON format for file storage
    - Deserialization: Converting JSON file data back to Python objects
    - CRUD: Create, Read, Update, Delete operations on records
    - Auto-increment ID: Each new record gets a unique sequential ID

References:
    - Real Python: The return Statement (early returns in loops)
      https://realpython.com/python-return-statement/
   -  Python Official Docs: Errors and Exceptions (8.3 Handling Exceptions)
      https://docs.python.org/3/tutorial/errors.html
    - Real Python: Context Managers (with statements)
      https://realpython.com/python-with-statement/
    - Real Python: List Comprehensions (filter/delete operations)
      https://realpython.com/list-comprehensions/
    - Real Python: Working with JSON (serialization)
      https://realpython.com/python-json/
    - Data Serialization — The Hitchhiker's Guide to Python (JSON, Pickle, and flat vs. nested data concepts)
      https://docs.python-guide.org/scenarios/serialization/ 
    - Python Official Docs: Control Flow
      https://docs.python.org/3/tutorial/controlflow.html
    - Python Official Docs: json module
      https://docs.python.org/3/library/json.html
    - Real Python: Reading and Writing Files in Python (context managers, encoding, file paths)
      https://realpython.com/read-write-files-python/      
    - PEP 8 Style Guide for Python Code
      https://www.python.org/dev/peps/pep-0008/
    - Real Python: Type Hints (function signatures)
      https://realpython.com/python-type-hints/
    - Real Python: pathlib (file path handling)
      https://realpython.com/python-pathlib/
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Backend directory to Python path so we can import models
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from models import create_record_from_dict


class RecordStorage:
    def __init__(self, filename: str):
        """Initialize storage with JSONL file"""
        self.path = Path(filename)

        # Create parent directory if it doesn't exist
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.records: List[Dict[str, Any]] = []
        self.load_records()

        print(f"Storage initialized with {len(self.records)} records")

    def load_records(self) -> None:
        """Load records from JSONL file (one JSON object per line)"""
        self.records = []

        if not self.path.exists():
            print(f"Data file {self.path} does not exist. Starting with empty records.")
            return

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue

                    try:
                        record_data = json.loads(line)
                        # Validate the record
                        record = create_record_from_dict(record_data)
                        self.records.append(record_data)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Warning: Skipping invalid record on line {line_num}: {e}")

            print(f"Loaded {len(self.records)} records from {self.path}")

        except Exception as e:
            print(f"Error loading records from {self.path}: {e}")
            self.records = []

    def save_records(self) -> None:
        """Save records to JSONL file (one JSON object per line)"""
        try:
            # Create backup if file exists
            backup_path = None
            if self.path.exists():
                backup_path = self.path.with_suffix('.jsonl.bak')
                if backup_path.exists():
                    backup_path.unlink()
                self.path.rename(backup_path)

            # Write all records as JSONL
            with open(self.path, 'w', encoding='utf-8') as f:
                for record in self.records:
                    json_line = json.dumps(record)
                    f.write(json_line + '\n')

            print(f"Saved {len(self.records)} records to {self.path}")

            # Remove backup if save was successful
            if backup_path and backup_path.exists():
                backup_path.unlink()

        except Exception as e:
            print(f"Error saving records: {e}")
            # Try to restore from backup
            if backup_path and backup_path.exists():
                print("Attempting to restore from backup...")
                backup_path.rename(self.path)
            raise

    def get_next_id(self, record_type: Optional[str] = None) -> int:
        """Get next available ID for a record type"""
        if not self.records:
            return 1

        if record_type:
            # Get max ID for specific type
            ids = [
                r['ID'] for r in self.records
                if r.get('Type') == record_type and isinstance(r.get('ID'), (int, float))
            ]
        else:
            # Get max ID overall
            ids = [r['ID'] for r in self.records if isinstance(r.get('ID'), (int, float))]

        return int(max(ids)) + 1 if ids else 1

    def add_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new record"""
        # Auto-assign ID if not provided
        if 'ID' not in record_data or not record_data['ID']:
            record_type = record_data.get('Type', '')
            record_data['ID'] = self.get_next_id(record_type)

        # Validate the record
        try:
            record = create_record_from_dict(record_data)
            record.validate()
        except ValueError as e:
            raise ValueError(f"Invalid record data: {e}")

        # Add to storage
        self.records.append(record_data)
        self.save_records()
        return record_data

    def get_record(self, record_id: int, record_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        for record in self.records:
            if record.get('ID') == record_id:
                if record_type and record.get('Type') != record_type:
                    continue
                return record
        return None

    def get_all_records(self, record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all records, optionally filtered by type"""
        if record_type:
            return [r for r in self.records if r.get('Type') == record_type]
        return self.records.copy()  # Return copy to prevent modification

    def update_record(self, record_id: int, record_type: str, update_data: Dict[str, Any]) -> bool:
        """Update a record"""
        for i, record in enumerate(self.records):
            if record.get('ID') == record_id and record.get('Type') == record_type:
                # Keep the ID and Type
                update_data['ID'] = record_id
                update_data['Type'] = record_type

                # Validate before updating
                try:
                    updated_record = create_record_from_dict(update_data)
                    updated_record.validate()
                except ValueError as e:
                    raise ValueError(f"Invalid update data: {e}")

                self.records[i] = update_data
                self.save_records()
                return True

        return False

    def delete_record(self, record_id: int, record_type: str) -> bool:
        """Delete a record"""
        initial_length = len(self.records)
        self.records = [
            r for r in self.records
            if not (r.get('ID') == record_id and r.get('Type') == record_type)
        ]

        if len(self.records) < initial_length:
            self.save_records()
            return True
        return False

    def search_records(self, record_type: str, field: str, value: str) -> List[Dict[str, Any]]:
        """Search records by field and value (case-insensitive)"""
        results = []
        search_value = value.lower()

        for record in self.records:
            if record.get('Type') != record_type:
                continue

            if field == 'all':
                # Search all string fields
                for field_value in record.values():
                    if isinstance(field_value, str) and search_value in field_value.lower():
                        results.append(record)
                        break
                    elif field_value is not None and search_value in str(field_value).lower():
                        results.append(record)
                        break
            elif field in record:
                # Search specific field
                field_value = record[field]
                if isinstance(field_value, str) and search_value in field_value.lower():
                    results.append(record)
                elif field_value is not None and search_value in str(field_value).lower():
                    results.append(record)

        return results

    def clear_all(self):
        """Clear all records"""
        self.records = []
        self.save_records()
        print("All records cleared")
