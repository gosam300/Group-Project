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
from typing import List, Dict, Any


# Configuration
STORAGE_FILE = Path("records.json")


class Storage:
    """
    Saving and loading data using JSON file storage.
    
    Records are kept in memory (self.records) while the program runs.
    Call load() to read from file and save() to write to file.
    """
    
    def __init__(self, file_path: Path = STORAGE_FILE):
        """Initialise Storage and load existing records from disk"""
        self.path = file_path
        self.records: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load records from JSON file. Return empty list if file doesn't exist or is corrupted"""
        if not self.path.exists():
            self.records = []
            return
        
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        except json.JSONDecodeError:
            # File corrupted, start fresh
            self.records = []
    
    def save(self):
        """Write all records to JSON file"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)
    
    def get_next_id(self) -> int:
        """Return the next available ID for a new record"""
        if not self.records:
            return 1
        
        max_id = max(r.get("id", 0) for r in self.records if isinstance(r.get("id"), int))
        return max_id + 1
    
    def create_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new record with auto-assigned ID. Does not save to disk"""
        record["id"] = self.get_next_id()
        self.records.append(record)
        return record
    
    def read_record(self, record_id: int) -> Dict[str, Any] | None:
        """Find and return a single record by ID. Returns None if not found"""
        for record in self.records:
            if record.get("id") == record_id:
                return record
        return None
    
    def update_record(self, record_id: int, updated_fields: Dict[str, Any]) -> bool:
        """Update a record's fields. Returns True if successful or False if record not found"""
        record = self.read_record(record_id)
        if record is None:
            return False
        record.update(updated_fields)
        return True
    
    def delete_record(self, record_id: int) -> bool:
        """Remove a record by ID. Returns True if deleted or False if not found"""
        before = len(self.records)
        self.records = [r for r in self.records if r.get("id") != record_id]
        return len(self.records) < before
    
    def search_records(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Find all records where a field matches a value (case-insensitive)"""
        results = []
        for record in self.records:
            record_value = str(record.get(field, "")).lower()
            search_value = str(value).lower()
            if record_value == search_value:
                results.append(record)
        return results
