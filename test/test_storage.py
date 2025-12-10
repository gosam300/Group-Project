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

import pytest
import json
import tempfile
from pathlib import Path
from src.data.record_storage import Storage, get_storage
from src.data.models import Client, Airline, Flight


class TestStorageInitialization:
    """Test storage initialization and file handling"""

    def test_storage_init_new_file(self):
        """Test initialization with non-existent file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "new_records.json"
            storage = Storage(file_path)

            assert len(storage.records) == 0
            assert storage.path == file_path
            assert not file_path.exists()  # File not created until save()

    def test_storage_init_existing_file(self):
        """Test initialization with existing valid file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "existing_records.json"

            # Create test data
            test_data = [
                {"Type": "client", "ID": 1, "Name": "Test Client"},
                {"Type": "airline", "ID": 1, "CompanyName": "Test Airline"}
            ]

            with open(file_path, 'w') as f:
                json.dump(test_data, f)

            storage = Storage(file_path)

            assert len(storage.records) == 2
            assert file_path.exists()

    def test_storage_init_corrupted_file(self):
        """Test initialization with corrupted JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "corrupted.json"

            # Write invalid JSON
            with open(file_path, 'w') as f:
                f.write("{invalid json")

            storage = Storage(file_path)

            # Should start with empty records
            assert len(storage.records) == 0

    def test_storage_load_legacy_format(self):
        """Test loading legacy format with separate lists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "legacy_records.json"

            # Legacy format
            test_data = {
                "clients": [
                    {"ID": 1, "Name": "Client 1", "PhoneNumber": "123"}
                ],
                "airlines": [
                    {"ID": 1, "CompanyName": "Airline 1"}
                ],
                "flights": [
                    {"ID": 1, "Client_ID": 1, "Airline_ID": 1,
                     "Date": "2024-12-15", "StartCity": "A", "EndCity": "B"}
                ]
            }

            with open(file_path, 'w') as f:
                json.dump(test_data, f)

            storage = Storage(file_path)

            assert len(storage.records) == 3
            assert any(isinstance(r, Client) for r in storage.records)
            assert any(isinstance(r, Airline) for r in storage.records)
            assert any(isinstance(r, Flight) for r in storage.records)

    def test_singleton_pattern(self):
        """Test get_storage returns singleton instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"

            storage1 = get_storage(file_path)
            storage2 = get_storage(file_path)

            assert storage1 is storage2
            assert storage1.path == storage2.path


class TestRecordCreation:
    """Test record creation functionality"""

    def test_create_record_client(self):
        """Test creating a client record"""
        storage = Storage()
        storage.clear_all()  # Start fresh

        client_data = {
            "Type": "client",
            "Name": "John Doe",
            "Phone Number": "555-1234",
            "City": "New York",
            "Country": "USA"
        }

        client = storage.create_record(client_data)

        assert isinstance(client, Client)
        assert client.ID == 1  # First record
        assert client.Name == "John Doe"
        assert len(storage.records) == 1

    def test_create_record_airline(self):
        """Test creating an airline record"""
        storage = Storage()
        storage.clear_all()

        airline_data = {
            "Type": "airline",
            "Company Name": "Delta Airlines"
        }

        airline = storage.create_record(airline_data)

        assert isinstance(airline, Airline)
        assert airline.ID == 1
        assert airline.CompanyName == "Delta Airlines"

    def test_create_record_flight(self):
        """Test creating a flight record"""
        storage = Storage()
        storage.clear_all()

        # First create client and airline
        storage.create_record({"Type": "client", "Name": "Client", "Phone Number": "123", "City": "A", "Country": "B"})
        storage.create_record({"Type": "airline", "Company Name": "Airline"})

        flight_data = {
            "Type": "flight",
            "Client_ID": 1,
            "Airline_ID": 2,  # IDs are sequential
            "Date": "2024-12-15T14:30:00",
            "Start City": "New York",
            "End City": "London"
        }

        flight = storage.create_record(flight_data)

        assert isinstance(flight, Flight)
        assert flight.ID == 3  # Third record
        assert flight.Client_ID == 1
        assert flight.Airline_ID == 2

    def test_create_record_invalid_type(self):
        """Test creating record with invalid type"""
        storage = Storage()
        storage.clear_all()

        invalid_data = {
            "Type": "invalid",
            "Name": "Test"
        }

        with pytest.raises(ValueError, match="Unknown record type"):
            storage.create_record(invalid_data)

    def test_create_record_validation_failure(self):
        """Test creating record that fails validation"""
        storage = Storage()
        storage.clear_all()

        invalid_client_data = {
            "Type": "client",
            "Name": "",  # Missing required field
            "Phone Number": "123"
        }

        with pytest.raises(ValueError):
            storage.create_record(invalid_client_data)

    def test_create_record_from_model(self):
        """Test creating record from model instance"""
        storage = Storage()
        storage.clear_all()

        client = Client(
            ID=999,  # Will be overridden
            Name="Model Client",
            PhoneNumber="555-9999",
            City="Test",
            Country="Test"
        )

        saved_client = storage.create_record_from_model(client)

        assert saved_client.ID != 999  # Should get new ID
        assert saved_client.Name == "Model Client"
        assert len(storage.records) == 1


class TestRecordRetrieval:
    """Test record retrieval functionality"""

    @pytest.fixture
    def populated_storage(self):
        """Create storage with test data"""
        storage = Storage()
        storage.clear_all()

        # Add test records
        storage.create_record({
            "Type": "client",
            "Name": "Client 1",
            "Phone Number": "111",
            "City": "City1",
            "Country": "Country1"
        })
        storage.create_record({
            "Type": "client",
            "Name": "Client 2",
            "Phone Number": "222",
            "City": "City2",
            "Country": "Country2"
        })
        storage.create_record({
            "Type": "airline",
            "Company Name": "Airline 1"
        })
        storage.create_record({
            "Type": "airline",
            "Company Name": "Airline 2"
        })

        return storage

    def test_read_record_existing(self, populated_storage):
        """Test reading existing record"""
        record = populated_storage.read_record(1)

        assert record is not None
        assert record.ID == 1
        assert isinstance(record, Client)
        assert record.Name == "Client 1"

    def test_read_record_nonexistent(self, populated_storage):
        """Test reading non-existent record"""
        record = populated_storage.read_record(999)
        assert record is None

    def test_read_record_with_type_filter(self, populated_storage):
        """Test reading record with type filter"""
        # Should find client with ID 1
        client = populated_storage.read_record(1, "client")
        assert isinstance(client, Client)

        # Should not find airline with ID 1 (that's ID 3)
        airline = populated_storage.read_record(1, "airline")
        assert airline is None

    def test_read_all_records(self, populated_storage):
        """Test reading all records"""
        records = populated_storage.read_all_records()
        assert len(records) == 4

    def test_read_all_records_with_type_filter(self, populated_storage):
        """Test reading all records with type filter"""
        clients = populated_storage.read_all_records("client")
        assert len(clients) == 2
        assert all(isinstance(r, Client) for r in clients)

        airlines = populated_storage.read_all_records("airline")
        assert len(airlines) == 2
        assert all(isinstance(r, Airline) for r in airlines)

        flights = populated_storage.read_all_records("flight")
        assert len(flights) == 0

    def test_read_clients(self, populated_storage):
        """Test reading only clients"""
        clients = populated_storage.read_clients()
        assert len(clients) == 2
        assert all(isinstance(r, Client) for r in clients)

    def test_read_airlines(self, populated_storage):
        """Test reading only airlines"""
        airlines = populated_storage.read_airlines()
        assert len(airlines) == 2
        assert all(isinstance(r, Airline) for r in airlines)

    def test_read_flights_empty(self, populated_storage):
        """Test reading flights when none exist"""
        flights = populated_storage.read_flights()
        assert len(flights) == 0


class TestRecordUpdate:
    """Test record update functionality"""

    @pytest.fixture
    def storage_with_client(self):
        """Create storage with a single client"""
        storage = Storage()
        storage.clear_all()

        storage.create_record({
            "Type": "client",
            "Name": "Original Name",
            "Phone Number": "555-1234",
            "City": "Original City",
            "Country": "Original Country"
        })

        return storage

    def test_update_record_success(self, storage_with_client):
        """Test successful record update"""
        updated = storage_with_client.update_record(1, {
            "Name": "Updated Name",
            "City": "Updated City"
        })

        assert updated is True

        # Verify update
        record = storage_with_client.read_record(1)
        assert record.Name == "Updated Name"
        assert record.City == "Updated City"
        assert record.PhoneNumber == "555-1234"  # Unchanged

    def test_update_record_nonexistent(self, storage_with_client):
        """Test updating non-existent record"""
        updated = storage_with_client.update_record(999, {"Name": "New Name"})
        assert updated is False

    def test_update_record_validation_failure(self, storage_with_client):
        """Test update that fails validation"""
        # Try to set name to empty string
        with pytest.raises(ValueError):
            storage_with_client.update_record(1, {"Name": ""})

        # Original record should remain unchanged
        record = storage_with_client.read_record(1)
        assert record.Name == "Original Name"

    def test_update_record_complete_overwrite(self, storage_with_client):
        """Test complete record overwrite"""
        new_data = {
            "Name": "Completely New",
            "Phone Number": "999-9999",
            "City": "New City",
            "Country": "New Country",
            "State": "NY",
            "Zip Code": "10001"
        }

        updated = storage_with_client.update_record(1, new_data)
        assert updated is True

        record = storage_with_client.read_record(1)
        assert record.Name == "Completely New"
        assert record.PhoneNumber == "999-9999"
        assert record.City == "New City"


class TestRecordDeletion:
    """Test record deletion functionality"""

    @pytest.fixture
    def storage_with_mixed_records(self):
        """Create storage with mixed record types"""
        storage = Storage()
        storage.clear_all()

        # Add records with different IDs
        storage.create_record({"Type": "client", "Name": "C1", "Phone Number": "1", "City": "A", "Country": "B"})
        storage.create_record({"Type": "client", "Name": "C2", "Phone Number": "2", "City": "A", "Country": "B"})
        storage.create_record({"Type": "airline", "Company Name": "A1"})
        storage.create_record({"Type": "airline", "Company Name": "A2"})

        return storage

    def test_delete_record_success(self, storage_with_mixed_records):
        """Test successful record deletion"""
        initial_count = len(storage_with_mixed_records.records)

        deleted = storage_with_mixed_records.delete_record(1)

        assert deleted is True
        assert len(storage_with_mixed_records.records) == initial_count - 1
        assert storage_with_mixed_records.read_record(1) is None

    def test_delete_record_nonexistent(self, storage_with_mixed_records):
        """Test deleting non-existent record"""
        initial_count = len(storage_with_mixed_records.records)

        deleted = storage_with_mixed_records.delete_record(999)

        assert deleted is False
        assert len(storage_with_mixed_records.records) == initial_count

    def test_delete_record_with_type(self, storage_with_mixed_records):
        """Test deletion with type specification"""
        # There's a client with ID 1
        deleted = storage_with_mixed_records.delete_record(1, "client")
        assert deleted is True

        # There's no airline with ID 1 (airlines start at ID 3)
        deleted = storage_with_mixed_records.delete_record(1, "airline")
        assert deleted is False

    def test_delete_client_flights(self):
        """Test deleting flights for a specific client"""
        storage = Storage()
        storage.clear_all()

        # Create client and airline
        storage.create_record({"Type": "client", "Name": "C1", "Phone Number": "1", "City": "A", "Country": "B"})
        storage.create_record({"Type": "airline", "Company Name": "A1"})

        # Create flights for client 1
        storage.create_record({
            "Type": "flight",
            "Client_ID": 1,
            "Airline_ID": 2,
            "Date": "2024-12-15",
            "Start City": "A",
            "End City": "B"
        })
        storage.create_record({
            "Type": "flight",
            "Client_ID": 1,
            "Airline_ID": 2,
            "Date": "2024-12-16",
            "Start City": "B",
            "End City": "C"
        })

        # Create another flight for different client (will add client)
        storage.create_record({"Type": "client", "Name": "C2", "Phone Number": "2", "City": "C", "Country": "D"})
        storage.create_record({
            "Type": "flight",
            "Client_ID": 3,  # Client 2
            "Airline_ID": 2,
            "Date": "2024-12-17",
            "Start City": "C",
            "End City": "D"
        })

        flights_deleted = storage.delete_client_flights(1)

        assert flights_deleted == 2
        flights = storage.read_flights()
        assert len(flights) == 1
        assert flights[0].Client_ID == 3  # Only flight for client 2 remains

    def test_delete_airline_flights(self):
        """Test deleting flights for a specific airline"""
        storage = Storage()
        storage.clear_all()

        # Create clients and airlines
        storage.create_record({"Type": "client", "Name": "C1", "Phone Number": "1", "City": "A", "Country": "B"})
        storage.create_record({"Type": "airline", "Company Name": "A1"})
        storage.create_record({"Type": "airline", "Company Name": "A2"})

        # Create flights for airline 2 (ID 3)
        storage.create_record({
            "Type": "flight",
            "Client_ID": 1,
            "Airline_ID": 3,  # Airline 2
            "Date": "2024-12-15",
            "Start City": "A",
            "End City": "B"
        })
        storage.create_record({
            "Type": "flight",
            "Client_ID": 1,
            "Airline_ID": 3,
            "Date": "2024-12-16",
            "Start City": "B",
            "End City": "C"
        })

        # Create flight for different airline
        storage.create_record({
            "Type": "flight",
            "Client_ID": 1,
            "Airline_ID": 2,  # Airline 1
            "Date": "2024-12-17",
            "Start City": "C",
            "End City": "D"
        })

        flights_deleted = storage.delete_airline_flights(3)

        assert flights_deleted == 2
        flights = storage.read_flights()
        assert len(flights) == 1
        assert flights[0].Airline_ID == 2


class TestSearchFunctionality:
    """Test search functionality"""

    @pytest.fixture
    def search_storage(self):
        """Create storage with searchable data"""
        storage = Storage()
        storage.clear_all()

        # Add clients
        storage.create_record({
            "Type": "client",
            "Name": "John Doe",
            "Phone Number": "555-1234",
            "City": "New York",
            "Country": "USA",
            "State": "NY"
        })
        storage.create_record({
            "Type": "client",
            "Name": "Jane Smith",
            "Phone Number": "555-5678",
            "City": "Los Angeles",
            "Country": "USA",
            "State": "CA"
        })
        storage.create_record({
            "Type": "client",
            "Name": "Bob Johnson",
            "Phone Number": "555-9012",
            "City": "London",
            "Country": "UK"
        })

        # Add airlines
        storage.create_record({
            "Type": "airline",
            "Company Name": "Delta Airlines"
        })
        storage.create_record({
            "Type": "airline",
            "Company Name": "British Airways"
        })

        return storage

    def test_search_records_exact_match(self, search_storage):
        """Test search with exact match"""
        results = search_storage.search_records("client", "City", "New York")

        assert len(results) == 1
        assert results[0]["Name"] == "John Doe"
        assert results[0]["City"] == "New York"

    def test_search_records_case_insensitive(self, search_storage):
        """Test case-insensitive search"""
        results = search_storage.search_records("client", "City", "new york")

        assert len(results) == 1
        assert results[0]["City"] == "New York"

    def test_search_records_substring(self, search_storage):
        """Test substring search"""
        results = search_storage.search_records("client", "Name", "john")

        assert len(results) == 1
        assert "John" in results[0]["Name"]

    def test_search_records_all_fields(self, search_storage):
        """Test search across all fields"""
        results = search_storage.search_records("client", "all", "555")

        # Should find all clients (all have 555 in phone)
        assert len(results) == 3

    def test_search_records_multiple_matches(self, search_storage):
        """Test search returning multiple matches"""
        results = search_storage.search_records("client", "Country", "USA")

        assert len(results) == 2
        names = {r["Name"] for r in results}
        assert "John Doe" in names
        assert "Jane Smith" in names

    def test_search_records_no_match(self, search_storage):
        """Test search with no matches"""
        results = search_storage.search_records("client", "City", "Tokyo")

        assert len(results) == 0

    def test_search_records_wrong_type(self, search_storage):
        """Test search with wrong record type"""
        results = search_storage.search_records("flight", "City", "New York")

        assert len(results) == 0

    def test_advanced_search_single_criteria(self, search_storage):
        """Test advanced search with single criteria"""
        results = search_storage.advanced_search(City="New York")

        assert len(results) == 1
        assert isinstance(results[0], Client)
        assert results[0].City == "New York"

    def test_advanced_search_multiple_criteria(self, search_storage):
        """Test advanced search with multiple criteria"""
        results = search_storage.advanced_search(Country="USA", State="NY")

        assert len(results) == 1
        client = results[0]
        assert client.Country == "USA"
        assert client.State == "NY"

    def test_advanced_search_empty_criteria(self, search_storage):
        """Test advanced search with empty criteria"""
        results = search_storage.advanced_search()

        # Should return all records
        assert len(results) == len(search_storage.records)


class TestStoragePersistence:
    """Test storage save/load persistence"""

    def test_save_and_load(self):
        """Test that saved records can be loaded back"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_save.json"

            # Create storage and add records
            storage1 = Storage(file_path)
            storage1.clear_all()

            storage1.create_record({
                "Type": "client",
                "Name": "Saved Client",
                "Phone Number": "555-1234",
                "City": "Test City",
                "Country": "Test Country"
            })
            storage1.create_record({
                "Type": "airline",
                "Company Name": "Saved Airline"
            })

            # Save to file
            storage1.save()
            assert file_path.exists()

            # Create new storage instance to load
            storage2 = Storage(file_path)

            # Verify loaded records
            assert len(storage2.records) == 2

            clients = storage2.read_clients()
            assert len(clients) == 1
            assert clients[0].Name == "Saved Client"

            airlines = storage2.read_airlines()
            assert len(airlines) == 1
            assert airlines[0].CompanyName == "Saved Airline"

    def test_save_empty_storage(self):
        """Test saving empty storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.json"

            storage = Storage(file_path)
            storage.clear_all()
            storage.save()

            # Should create file
            assert file_path.exists()

            # Load back
            storage2 = Storage(file_path)
            assert len(storage2.records) == 0


class TestStatisticsAndUtilities:
    """Test statistics and utility functions"""

    def test_get_statistics(self):
        """Test getting storage statistics"""
        storage = Storage()
        storage.clear_all()

        # Add some records
        storage.create_record({"Type": "client", "Name": "C1", "Phone Number": "1", "City": "A", "Country": "B"})
        storage.create_record({"Type": "client", "Name": "C2", "Phone Number": "2", "City": "B", "Country": "C"})
        storage.create_record({"Type": "airline", "Company Name": "A1"})
        storage.create_record({"Type": "airline", "Company Name": "A2"})
        storage.create_record({"Type": "flight", "Client_ID": 1, "Airline_ID": 3,
                               "Date": "2024-12-15", "Start City": "A", "End City": "B"})
        storage.create_record({"Type": "flight", "Client_ID": 2, "Airline_ID": 4,
                               "Date": "2024-12-16", "Start City": "B", "End City": "C"})

        stats = storage.get_statistics()

        assert stats['total_records'] == 6
        assert stats['clients'] == 2
        assert stats['airlines'] == 2
        assert stats['flights'] == 2
        assert 'flight_cities' in stats
        assert stats['flight_cities']['unique_start_cities'] == 2
        assert stats['flight_cities']['unique_end_cities'] == 2

    def test_clear_all(self):
        """Test clearing all records"""
        storage = Storage()

        # Add some records
        storage.create_record({"Type": "client", "Name": "C1", "Phone Number": "1", "City": "A", "Country": "B"})
        assert len(storage.records) > 0

        storage.clear_all()
        assert len(storage.records) == 0

    def test_get_next_id_empty(self):
        """Test getting next ID from empty storage"""
        storage = Storage()
        storage.clear_all()

        assert storage.get_next_id() == 1
        assert storage.get_next_id("client") == 1
        assert storage.get_next_id("airline") == 1

    def test_get_next_id_with_records(self):
        """Test getting next ID with existing records"""
        storage = Storage()
        storage.clear_all()

        # Add records with specific IDs
        storage.create_record(
            {"Type": "client", "ID": 5, "Name": "C1", "Phone Number": "1", "City": "A", "Country": "B"})
        storage.create_record({"Type": "airline", "ID": 10, "Company Name": "A1"})

        # Next client ID should be 6
        assert storage.get_next_id("client") == 6

        # Next airline ID should be 11
        assert storage.get_next_id("airline") == 11

        # Next overall ID should be 11 (max of 5 and 10 is 10, plus 1)
        assert storage.get_next_id() == 11


class TestImportExport:
    """Test import/export functionality"""

    def test_export_to_file(self):
        """Test exporting records to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Storage()
            storage.clear_all()

            # Add test records
            storage.create_record(
                {"Type": "client", "Name": "Export Test", "Phone Number": "123", "City": "A", "Country": "B"})

            export_path = Path(tmpdir) / "export.json"
            storage.export_to_file(export_path)

            assert export_path.exists()

            # Verify exported content
            with open(export_path, 'r') as f:
                exported = json.load(f)

            assert len(exported) == 1
            assert exported[0]['Name'] == "Export Test"

    def test_import_from_file_replace(self):
        """Test importing records with replacement"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create export file
            export_data = [
                {"Type": "client", "ID": 100, "Name": "Imported Client",
                 "Phone Number": "999", "City": "Import City", "Country": "Import Country"}
            ]

            import_path = Path(tmpdir) / "import.json"
            with open(import_path, 'w') as f:
                json.dump(export_data, f)

            # Create storage with existing data
            storage = Storage()
            storage.clear_all()
            storage.create_record(
                {"Type": "client", "Name": "Original", "Phone Number": "111", "City": "A", "Country": "B"})

            # Import (should replace)
            storage.import_from_file(import_path, merge=False)

            assert len(storage.records) == 1
            assert storage.records[0].Name == "Imported Client"

    def test_import_from_file_merge(self):
        """Test importing records with merge"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create import file
            import_data = [
                {"Type": "client", "ID": 100, "Name": "Imported Client",
                 "Phone Number": "999", "City": "Import City", "Country": "Import Country"}
            ]

            import_path = Path(tmpdir) / "import.json"
            with open(import_path, 'w') as f:
                json.dump(import_data, f)

            # Create storage with existing data
            storage = Storage()
            storage.clear_all()
            storage.create_record(
                {"Type": "client", "Name": "Original", "Phone Number": "111", "City": "A", "Country": "B"})

            # Import with merge
            storage.import_from_file(import_path, merge=True)

            assert len(storage.records) == 2
            names = {r.Name for r in storage.records}
            assert "Original" in names
            assert "Imported Client" in names


class TestErrorHandling:
    """Test error handling edge cases"""

    def test_duplicate_id_handling(self):
        """Test handling of duplicate IDs"""
        storage = Storage()
        storage.clear_all()

        # Manually add record with duplicate ID
        client1 = Client(ID=1, Name="Client 1", PhoneNumber="111", City="A", Country="B")
        client2 = Client(ID=1, Name="Client 2", PhoneNumber="222", City="B", Country="C")  # Same ID!

        storage.create_record_from_model(client1)

        # This should get a new ID
        saved_client2 = storage.create_record_from_model(client2)

        assert saved_client2.ID != 1
        assert saved_client2.Name == "Client 2"
        assert len(storage.records) == 2

    def test_corrupted_save(self):
        """Test handling of save errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory with the same name as our target file
            file_path = Path(tmpdir) / "records.json"
            file_path.mkdir()  # Create directory instead of file

            storage = Storage(file_path)

            # Save should handle the error gracefully
            try:
                storage.save()
            except Exception as e:
                # Should log error but not crash
                print(f"Save error (expected): {e}")

    def test_invalid_field_access(self):
        """Test accessing invalid fields"""
        storage = Storage()
        storage.clear_all()

        # Search for non-existent field
        results = storage.search_records("client", "nonexistent_field", "value")
        assert len(results) == 0  # Should return empty list, not crash


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
