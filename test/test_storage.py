"""
Unit tests for Storage class (File I/O and Record Persistence)

Tests verify that the Storage class correctly handles JSON-based persistence
of records, including CRUD operations, file I/O, and ID management.

References:
    - PEP 8 Style Guide for Python Code
      https://www.python.org/dev/peps/pep-0008/
    - Python unittest documentation
      https://docs.python.org/3/library/unittest.html
    - Real Python: Getting Started With Testing
      https://realpython.com/python-testing/
    - Python tempfile documentation (test isolation)
      https://docs.python.org/3/library/tempfile.html
"""

import unittest
from pathlib import Path
from storage import Storage


class TestStorage(unittest.TestCase):
    """Test the Storage class"""
    
    def setUp(self):
        """Create a test storage file before each test"""
        self.test_file = Path("test_records.json")
        if self.test_file.exists():
            self.test_file.unlink()
    
    def tearDown(self):
        """Clean up test file after each test"""
        if self.test_file.exists():
            self.test_file.unlink()
    
    def test_create_empty_storage(self):
        """Storage initialises with empty list when file does not exist"""
        storage = Storage(self.test_file)
        self.assertEqual(len(storage.records), 0)
    
    def test_save_and_load(self):
        """Records are saved to file and loaded correctly"""
        storage = Storage(self.test_file)
        storage.create_record({"type": "client", "name": "Brett"})
        storage.save()
        
        storage2 = Storage(self.test_file)
        self.assertEqual(len(storage2.records), 1)
        self.assertEqual(storage2.records[0]["name"], "Brett")
    
    def test_auto_increment_id(self):
        """New records get sequential IDs starting at 1"""
        storage = Storage(self.test_file)
        rec1 = storage.create_record({"type": "client", "name": "Vu"})
        rec2 = storage.create_record({"type": "client", "name": "Morten"})
        
        self.assertEqual(rec1["id"], 1)
        self.assertEqual(rec2["id"], 2)
    
    def test_read_record(self):
        """Read operation returns the correct record by ID"""
        storage = Storage(self.test_file)
        storage.create_record({"type": "client", "name": "Ali"})
        
        record = storage.read_record(1)
        self.assertIsNotNone(record)
        self.assertEqual(record["name"], "Ali")
    
    def test_read_nonexistent_record(self):
        """Read returns None if there is a non-existent record"""
        storage = Storage(self.test_file)
        record = storage.read_record(999)
        self.assertIsNone(record)
    
    def test_update_record(self):
        """Update operation modifies record fields"""
        storage = Storage(self.test_file)
        storage.create_record({"type": "client", "name": "Elias", "city": "London"})
        
        success = storage.update_record(1, {"city": "Manchester"})
        self.assertTrue(success)
        
        record = storage.read_record(1)
        self.assertEqual(record["city"], "Manchester")
    
    def test_update_nonexistent_record(self):
        """Update returns False if there is a non-existent record"""
        storage = Storage(self.test_file)
        success = storage.update_record(999, {"name": "Test"})
        self.assertFalse(success)
    
    def test_delete_record(self):
        """Delete operation removes record by ID"""
        storage = Storage(self.test_file)
        storage.create_record({"type": "client", "name": "George"})
        
        success = storage.delete_record(1)
        self.assertTrue(success)
        self.assertEqual(len(storage.records), 0)
    
    def test_delete_nonexistent_record(self):
        """Delete returns False if there is a non-existent record"""
        storage = Storage(self.test_file)
        success = storage.delete_record(999)
        self.assertFalse(success)
    
    def test_search_records(self):
        """Search returns the matching records by field value"""
        storage = Storage(self.test_file)
        storage.create_record({"type": "client", "name": "Frank", "city": "Stavanger"})
        storage.create_record({"type": "client", "name": "Lene", "city": "Bandar Seri Begawan"})
        
        results = storage.search_records("city", "Stavanger")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Frank")


if __name__ == "__main__":
    unittest.main(verbosity=2)
