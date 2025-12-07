import pytest
import tempfile
from pathlib import Path
from src.data.models import Client, Airline, Flight
from src.data.record_storage import RecordStorage


class TestIntegration:
    """Integration tests for models and storage"""

    def test_end_to_end_workflow(self):
        """Test complete workflow from creation to storage and retrieval"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "integration_test.json"

            # Initialize storage
            storage = RecordStorage(file_path)
            storage.clear_all()

            # 1. Create and save client
            client_data = {
                "Type": "client",
                "Name": "Integration Client",
                "Phone Number": "555-INTEGRATION",
                "Address Line 1": "123 Integration St",
                "City": "Integration City",
                "State": "IC",
                "Zip Code": "12345",
                "Country": "Integrationland"
            }

            client = storage.create_record(client_data)
            assert client.ID == 1

            # 2. Create and save airline
            airline_data = {
                "Type": "airline",
                "Company Name": "Integration Airlines"
            }

            airline = storage.create_record(airline_data)
            assert airline.ID == 2

            # 3. Create and save flight linking client and airline
            flight_data = {
                "Type": "flight",
                "Client_ID": client.ID,
                "Airline_ID": airline.ID,
                "Date": "2024-12-15T14:30:00",
                "Start City": "Integration City",
                "End City": "Destination City"
            }

            flight = storage.create_record(flight_data)
            assert flight.ID == 3
            assert flight.Client_ID == 1
            assert flight.Airline_ID == 2

            # 4. Save to disk
            storage.save()

            # 5. Create new storage instance and load
            storage2 = RecordStorage(file_path)

            # 6. Verify loaded data
            assert len(storage2.records) == 3

            loaded_client = storage2.read_record(1, "client")
            assert isinstance(loaded_client, Client)
            assert loaded_client.Name == "Integration Client"
            assert loaded_client.PhoneNumber == "555-INTEGRATION"

            loaded_airline = storage2.read_record(2, "airline")
            assert isinstance(loaded_airline, Airline)
            assert loaded_airline.CompanyName == "Integration Airlines"

            loaded_flight = storage2.read_record(3, "flight")
            assert isinstance(loaded_flight, Flight)
            assert loaded_flight.StartCity == "Integration City"
            assert loaded_flight.Client_ID == 1
            assert loaded_flight.Airline_ID == 2

            # 7. Test search
            search_results = storage2.search_records("client", "City", "Integration")
            assert len(search_results) == 1
            assert search_results[0]["Name"] == "Integration Client"

            # 8. Test update
            storage2.update_record(1, {"City": "Updated Integration City"})
            updated_client = storage2.read_record(1)
            assert updated_client.City == "Updated Integration City"

            # 9. Test delete
            deleted = storage2.delete_record(3, "flight")
            assert deleted is True
            assert len(storage2.read_flights()) == 0

            # 10. Final save and verify
            storage2.save()

            # Load one more time to verify persistence
            storage3 = RecordStorage(file_path)
            assert len(storage3.records) == 2  # Flight deleted
            assert len(storage3.read_clients()) == 1
            assert len(storage3.read_airlines()) == 1

    def test_concurrent_id_generation(self):
        """Test that IDs are generated correctly with mixed record types"""
        storage = RecordStorage()
        storage.clear_all()

        # Create records in mixed order
        client1 = storage.create_record({
            "Type": "client",
            "Name": "Client 1",
            "Phone Number": "111",
            "City": "A",
            "Country": "B"
        })
        assert client1.ID == 1

        airline1 = storage.create_record({
            "Type": "airline",
            "Company Name": "Airline 1"
        })
        assert airline1.ID == 2

        client2 = storage.create_record({
            "Type": "client",
            "Name": "Client 2",
            "Phone Number": "222",
            "City": "C",
            "Country": "D"
        })
        assert client2.ID == 3  # Next client ID, not 3 overall

        airline2 = storage.create_record({
            "Type": "airline",
            "Company Name": "Airline 2"
        })
        assert airline2.ID == 4  # Next airline ID

        # Verify counts
        assert len(storage.read_clients()) == 2
        assert len(storage.read_airlines()) == 2

        # Verify IDs
        client_ids = {c.ID for c in storage.read_clients()}
        assert client_ids == {1, 3}

        airline_ids = {a.ID for a in storage.read_airlines()}
        assert airline_ids == {2, 4}

    def test_dependent_data_consistency(self):
        """Test that dependent data (flights) are handled correctly"""
        storage = RecordStorage()
        storage.clear_all()

        # Create client and airline
        client = storage.create_record({
            "Type": "client",
            "Name": "Test Client",
            "Phone Number": "111",
            "City": "A",
            "Country": "B"
        })

        airline = storage.create_record({
            "Type": "airline",
            "Company Name": "Test Airline"
        })

        # Create flights
        flight1 = storage.create_record({
            "Type": "flight",
            "Client_ID": client.ID,
            "Airline_ID": airline.ID,
            "Date": "2024-12-15",
            "Start City": "A",
            "End City": "B"
        })

        flight2 = storage.create_record({
            "Type": "flight",
            "Client_ID": client.ID,
            "Airline_ID": airline.ID,
            "Date": "2024-12-16",
            "Start City": "B",
            "End City": "C"
        })

        # Verify flights exist
        assert len(storage.read_flights()) == 2

        # Delete client (should also delete flights)
        deleted = storage.delete_record(client.ID, "client")
        assert deleted is True

        # Verify flights are also deleted
        assert len(storage.read_flights()) == 0

        # Create new client and airline
        new_client = storage.create_record({
            "Type": "client",
            "Name": "New Client",
            "Phone Number": "222",
            "City": "C",
            "Country": "D"
        })

        new_airline = storage.create_record({
            "Type": "airline",
            "Company Name": "New Airline"
        })

        # Create new flight
        new_flight = storage.create_record({
            "Type": "flight",
            "Client_ID": new_client.ID,
            "Airline_ID": new_airline.ID,
            "Date": "2024-12-17",
            "Start City": "C",
            "End City": "D"
        })

        # Delete airline (should delete flight)
        deleted = storage.delete_record(new_airline.ID, "airline")
        assert deleted is True
        assert len(storage.read_flights()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

