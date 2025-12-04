# Record Management System: Storage Module

## Project Overview

This is the storage layer for a Record Management System built to manage client, airline, and flight records. 
The storage module manages saving and loading record data to/from a JSON file, providing a complete CRUD (Create, Read, Update, Delete) interface with search functionality.

## Storage Module Purpose

The storage module manages saving and loading record data to/from a JSON file. 
Records are stored in memory while the program runs. Call save() to write them to disk.

## Project Structure

```
src/
├── storage.py                  # Saving and loading record data
tests/
├── test_storage.py             # Unit tests for storage module
records.json                    # JSON file for record (created at runtime)
```

## Module Features

- **CRUD Operations:** Create, read, update, and delete records
- **Auto-increment IDs:** Each new record automatically receives a unique sequential ID
- **Search Functionality:** Find records by field value with case-insensitive matching
- **JSON Persistence:** Records saved to and loaded from JSON file
- **Error Handling:** Handles corrupted files and missing data
- **Context Managers:** Uses with statements for safe file handling

## Design Decisions

### Global ID
IDs are globally unique across all record types. The `get_next_id()` method tracks the highest ID in the entire records list, not per-type. The API—callers only need to know the record ID (and not the type).

**Why:** Simpler code and easier integration with data_manager and GUI.

### Type Checking in ID Generation
The `get_next_id()` method includes `isinstance()` checks to validate IDs before using them. If a record has a incorrect ID (string, null, or missing), it's skipped instead of crashing.
**Why:**  The app don't crash if records.json gets corrupted mid-save.

### Guard Clauses for Early Returns
Methods like `load()` and `get_next_id()` use guard clauses—checking for problem cases first, then returning early.
**Why:** More readable code and easier for team members to understand and modify.

### Public Methods
Core methods like `load()` and `get_next_id()` are public (no underscore prefix), not private. This allows data_manager and tests to call them when needed.
**Why:** Flexibility, other modules can reload data or check the next ID without workarounds. 

### Validation at Storage Level
This module does NOT validate record schemas (e.g., checking if Client has a Name field). That responsibility belongs to data_manager.
**Why:** Storage is focused on file I/O. Business logic and validation at the data_manager level.

## Running the Code

### Using Storage file in Your Code

```python
from storage import Storage

# Create storage instance (auto-loads from records.json)
storage = Storage()

# Create a new record
record = storage.create_record({"type": "client", "name": "George"})

# Read a record by ID
client = storage.read_record(1)

# Update a record
storage.update_record(1, {"name": "Vu"})

# Delete a record
storage.delete_record(1)

# Search records
results = storage.search_records("name", "Elias")

# Reload data from file
storage.load()

# Save to file
storage.save()

# Check next available ID
next_id = storage.get_next_id()
```

## Testing - Unit Tests

Test the storage module:

```bash
python -m pytest tests/test_storage.py -v
```

The unit tests cover:
- Creating records with auto-assigned IDs
- Reading records by ID
- Updating record fields
- Deleting records
- Searching with case-insensitive matching
- File I/O and persistence
- Error handling for corrupted files

## Storage API

### Core Methods

```python
storage = Storage()                           # Initialize and load from file
storage.create_record(data)                   # Create new record, returns record with ID
storage.read_record(record_id)                # Read record, returns record or None
storage.update_record(record_id, fields)      # Update fields, returns True/False
storage.delete_record(record_id)              # Delete record, returns True/False
storage.search_records(field, value)          # Search records, returns list
storage.save()                                # Persist all records to JSON file
storage.load()                                # Load records from JSON file
storage.get_next_id()                         # Get next available ID
```

## Integration Notes

### For Elias (data_manager)
- Storage does NOT validate schemas. Validate using models.py before calling storage.create_record().
- Use `storage.get_next_id()` if you need to know the ID before creating a record.

### For Ali (GUI)
- Should GUI call storage directly, or through data_manager?
- If GUI calls storage directly, need update gui.py (if you are using that George's template file) to use the new API names (create_record vs create, etc.).


